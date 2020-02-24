import os
import json
import logging
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Google Photos APIs リファレンス
# https://developers.google.com/photos/library/reference/rest


class GooglePhotos:
    # APIのURLやスコープ
    api_url = {
        "searchItems": "https://photoslibrary.googleapis.com/v1/mediaItems:search",
        "mediaItem": "https://photoslibrary.googleapis.com/v1/mediaItems/{}",
        "albums": "https://photoslibrary.googleapis.com/v1/albums",
    }
    scope = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
    sleep_time = 2
    # sleep_time = 10
    photo_download_format = "{base}=w{width}-h{height}"
    video_download_format = "{base}=dv"
    db_file = "/tmp/mmgphotos.db"
    db_table = "downloaded_media"

    def __init__(
        self,
        token_path="/tmp/mmgphotos_token.json",
        credential_path="/tmp/mmgphotos_client_secret.json",
        dotenv_path: str = None,
    ):
        load_dotenv(dotenv_path=dotenv_path, verbose=True)

        self._token_path = token_path
        self._google_session, logged_in = self._login(credential_path)
        # ログイン処理が行われていたらトークンを保存
        # 本来自動保存だが動かないので追加
        if logged_in:
            self._save_token()
        # 有効期限の過ぎたトークンをリフレッシュ
        self._token_expires_at = datetime.fromtimestamp(
            self._google_session.token.get("expires_at")
        )
        self._check_and_refresh_token()

    # ログイン後に取得したトークンをtoken.jsonに保存
    def _save_token(self):
        logger.debug("トークンを保存しています")
        Path(self._token_path).write_text(json.dumps(self._google_session.token))

    # token.jsonが存在したら読み込み
    def _load_token(self):
        # 存在しない場合は期限切れのダミーを返す
        token = {
            "access_token": "",
            "refresh_token": "",
            "token_type": "",
            "expires_in": "-30",
            "expires_at": (datetime.now() - timedelta(hours=2)).timestamp(),
        }
        path = Path(self._token_path)

        if "mmgphotos_token_contents" in os.environ:
            # .envから読み込む
            token = json.loads(os.environ["mmgphotos_token_contents"])
        elif path.exists():
            logger.debug("トークンをファイルから読み込んでいます")
            token = json.loads(path.read_text())
        return token

    def _check_and_refresh_token(self):
        if datetime.now() + timedelta(minutes=10) > self._token_expires_at:
            logger.debug("トークンの期限切れが近いため、更新を行います")
            new_token = self._google_session.refresh_token(
                self._google_session.auto_refresh_url, **self._google_session.auto_refresh_kwargs
            )
            self._google_session.token = new_token
            self._token_expires_at = datetime.fromtimestamp(
                self._google_session.token.get("expires_at")
            )

    def _get(self, *args, **kwargs):
        self._check_and_refresh_token()
        return self._google_session.get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        self._check_and_refresh_token()
        return self._google_session.post(*args, **kwargs)

    def _save_credential_from_env(self, credential_path):
        logger.debug("認証情報を保存しています")
        credential = os.environ.get("mmgphotos_client_secret_contents", "dummy")
        Path(credential_path).write_text(credential)

    # ログインしてセッションオブジェクトを返す
    def _login(self, credential_path):
        # 認証情報を環境変数から書き込み
        self._save_credential_from_env(credential_path)
        # 認証情報を読み込み
        auth_info = json.loads(Path(credential_path).read_text()).get("installed", None)
        assert auth_info is not None
        # トークン読み込み
        token = self._load_token()
        # トークン更新用の認証情報
        extras = {
            "client_id": auth_info.get("client_id"),
            "client_secret": auth_info.get("client_secret"),
        }
        # セッションオブジェクトを作成
        # TODO: token_updaterの引数がたぶん合わない
        google_session = OAuth2Session(
            auth_info.get("client_id"),
            scope=GooglePhotos.scope,
            token=token,
            auto_refresh_kwargs=extras,
            token_updater=self._save_token,
            auto_refresh_url=auth_info.get("token_uri"),
            redirect_uri=auth_info.get("redirect_uris")[0],
        )
        # ログインしていない場合ログインを行う
        logged_in = False
        if not google_session.authorized:
            logger.debug("ログインを行います")
            authorization_url, state = google_session.authorization_url(
                auth_info.get("auth_uri"), access_type="offline", prompt="select_account"
            )
            # 認証URLにアクセスしてコードをペースト
            print("Access {} and paste code.".format(authorization_url))
            access_code = input(">>> ")
            google_session.fetch_token(
                auth_info.get("token_uri"),
                client_secret=auth_info.get("client_secret"),
                code=access_code,
            )
            assert google_session.authorized
            logged_in = True
        return google_session, logged_in

    def get_album_list(self, page_num=10, page_size="50"):
        album_list = []
        params = {"pageSize": str(page_size)}
        for page_index in range(0, page_num):
            logger.debug("{}番目のページを取得します".format(page_index + 1))
            # リクエスト送信
            response = self._get(GooglePhotos.api_url.get("albums"))
            assert response.status_code == 200, "Response is not 200"
            res_json = response.json()
            # アルバム情報だけ抜き出し
            album_items = res_json.get("albums")
            album_list.extend(album_items)
            # 次ページのトークンを取得・設定
            if "nextPageToken" in res_json:
                params["pageToken"] = res_json.get("nextPageToken")
            else:
                break
            # 過負荷を避けるため間隔を開けてAPIを叩く
            time.sleep(GooglePhotos.sleep_time)
        return album_list

    def get_media_list(self, page_num=10, page_size="100", album_id=None, media="PHOTO"):
        media_list = []

        # パラメータ
        params = {"pageSize": str(page_size)}
        # リクエストボディ: アルバム指定(albumId)とfiltersは同時指定できない
        if album_id is not None:
            query_filter = {"albumId": album_id}
        else:
            query_filter = {"filters": {"mediaTypeFilter": {"mediaTypes": [media]}}}

        for page_index in range(0, page_num):
            logger.debug("{}番目のページを取得します".format(page_index + 1))
            # リクエスト送信
            api_url = GooglePhotos.api_url.get("searchItems")
            response = self._post(api_url, params=params, data=json.dumps(query_filter))
            assert response.status_code == 200, "Response is not 200"
            res_json = response.json()
            # 画像情報だけ抜き出し
            media_items = res_json.get("mediaItems")
            media_list.extend(media_items)
            # 次ページのトークンを取得・設定
            if "nextPageToken" in res_json:
                params["pageToken"] = res_json.get("nextPageToken")
            else:
                break
            # 過負荷を避けるため間隔を開けてAPIを叩く
            time.sleep(GooglePhotos.sleep_time)
        return media_list

    def download_media(self, media_id: str, save_dir: str = "./") -> Tuple[str, Optional[str]]:
        logger.debug("Downloading: {}".format(media_id))
        response = self._get(GooglePhotos.api_url["mediaItem"].format(media_id))
        assert response.status_code == 200
        media_item_latest = response.json()

        # MediaItemから各種情報を取得
        base_url = media_item_latest.get("baseUrl")
        metadata = media_item_latest.get("mediaMetadata")
        filename = media_item_latest.get("filename")
        description = media_item_latest.get("description", self._get_default_description())

        # ダウンロードURLを構成
        if "video" in metadata:
            logger.debug("This is video.")
            download_url = GooglePhotos.video_download_format.format(base=base_url)
        else:
            logger.debug("This is image.")
            download_url = GooglePhotos.photo_download_format.format(
                base=base_url, width=metadata["width"], height=metadata["height"]
            )

        # ダウンロード実行
        # if overwrite or not write_path.exists():
        if not self._is_already_downloaded(media_id):
            logger.debug("Download target is not exist. try to save...")
            self._save_downlod_info(media_id, filename)
            logger.debug("Donwload file. URL={}".format(download_url))
            response = self._get(download_url)
            assert response.status_code == 200
            # 保存
            write_path: Path = Path(save_dir) / filename
            # 存在していたら削除
            if write_path.exists():
                write_path.unlink()
            write_path.write_bytes(response.content)
            logger.debug("Saving to {}".format(write_path))

            return description, "{}".format(write_path)
        else:
            logger.debug("Download target is already exists. not save.")

            return description, None

    def _get_default_description(self):
        now = datetime.now()
        return "{0:%Y/%m/%d} 説明がありません".format(now)

    def _save_downlod_info(self, id: str, file: str) -> None:
        connector = sqlite3.connect(GooglePhotos.db_file)
        sql = "create table if not exists {}(id text, file text)".format(GooglePhotos.db_table)
        connector.execute(sql)
        sql = "insert into {} values('{}', '{}')".format(GooglePhotos.db_table, id, file)
        connector.execute(sql)
        connector.commit()
        connector.close()

    def _is_already_downloaded(self, search_id: str) -> bool:
        hit = False

        connector = sqlite3.connect(GooglePhotos.db_file)
        sql = "create table if not exists {}(id text, file text)".format(GooglePhotos.db_table)
        connector.execute(sql)
        cursor = connector.cursor()
        cursor.execute("select * from {} order by id".format(GooglePhotos.db_table))
        result = cursor.fetchall()
        for row in result:
            id = row[0]
            logger.debug("Hit sqlite db. id={}, file={}".format(id, row[1]))
            if search_id == id:
                hit = True
        cursor.close()
        connector.close()

        return hit
