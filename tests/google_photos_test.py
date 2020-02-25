import os
import pytest
import shutil
from pathlib import Path
from mmgphotos.google_photos import GooglePhotos


class TestGooglePhotos:
    @pytest.fixture()
    def gphotos1(self) -> GooglePhotos:
        return GooglePhotos()

    @pytest.mark.slow
    def test_get_album_list(self, gphotos1: GooglePhotos):
        gphotos1.get_album_list(page_num=2)

    @pytest.mark.slow
    def test_get_media_list_1(self, gphotos1: GooglePhotos):
        gphotos1.get_media_list(page_num=2)

    @pytest.mark.slow
    def test_get_media_list_2(self, gphotos1: GooglePhotos):
        # 「YouTubeUploaded」のalbum ID
        # AMx6VGH3q5mYvV2wQi97KcjHfPizyc19AzmS3efwYlC28HMzDBIQTXqp61g84qLZH7PY-Ue8TYDA
        gphotos1.get_media_list(
            page_num=1,
            album_id="AMx6VGH3q5mYvV2wQi97KcjHfPizyc19AzmS3efwYlC28HMzDBIQTXqp61g84qLZH7PY-Ue8TYDA",
            media="VIDEO",
        )

    @pytest.mark.slow
    def test_download_media(self, gphotos1: GooglePhotos):
        # ---------------
        # 事前準備
        # ---------------
        # 保存フォルダを削除
        save_dir = Path("./save")
        if save_dir.exists():
            shutil.rmtree(save_dir)
        save_dir.mkdir()
        # sqlite dbを削除
        db = Path("/tmp/mmgphotos.db")
        if db.exists():
            db.unlink()

        media_list = gphotos1.get_media_list(
            page_num=1,
            album_id="AMx6VGH3q5mYvV2wQi97KcjHfPizyc19AzmS3efwYlC28HMzDBIQTXqp61g84qLZH7PY-Ue8TYDA",
            media="VIDEO",
        )

        for media_info in media_list:
            description, download_file = gphotos1.download_media(
                media_info.get("id", "not_found"), save_dir=str(save_dir)
            )
            assert download_file is not None
            assert description is not None
            path = Path(download_file)
            assert path.exists()

            # 取り敢えず1個テストすれば良い
            break

    def default_description(self, gphotos1):
        result = gphotos1._get_default_description()
        print(result)

    def test_update_remote_db_file(self, gphotos1: GooglePhotos):
        os.environ["mmgphotos_db_file_s3_key_name"] = "mmgphotos/mmgphotos.db"
        gphotos1._update_remote_db_file()

    def test_update_local_db_file(self, gphotos1: GooglePhotos):
        os.environ["mmgphotos_db_file_s3_key_name"] = "mmgphotos/mmgphotos.db"
        gphotos1._update_local_db_file()
