import pytest
from mmgphotos.s3_accesser import S3Accesser


class TestS3Accesser:
    @pytest.fixture()
    def accessor1(self):
        return S3Accesser("magarimame")

    def test_download_and_upload(self, accessor1):
        accessor1.download("mmgphotos/mmgphotos-test.db", "/tmp/mmgphotos-test.db")
        accessor1.upload("/tmp/mmgphotos-test.db", "mmgphotos/mmgphotos-test.db")
