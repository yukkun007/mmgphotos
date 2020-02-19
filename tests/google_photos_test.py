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
        db = Path("./google_photos.db")
        if db.exists():
            db.unlink()

        media_list = gphotos1.get_media_list(
            page_num=1,
            album_id="AMx6VGH3q5mYvV2wQi97KcjHfPizyc19AzmS3efwYlC28HMzDBIQTXqp61g84qLZH7PY-Ue8TYDA",
            media="VIDEO",
        )

        for media_info in media_list:
            download_file = gphotos1.download_media(
                media_info.get("id", "not_found"), save_dir=str(save_dir)
            )
            assert download_file is not None
            path = Path(download_file)
            assert path.exists()
