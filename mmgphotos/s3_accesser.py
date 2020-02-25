import boto3


class S3Accesser:
    def __init__(self, bucket_name: str = "magarimame"):
        # バケット名
        self._bucket_name = bucket_name
        # バケット
        s3 = boto3.resource("s3")
        self.bucket = s3.Bucket(bucket_name)

    def upload(self, file_path: str, key_name: str) -> None:
        self.bucket.upload_file(file_path, key_name)

    def download(self, key_name: str, file_path: str) -> None:
        self.bucket.download_file(key_name, file_path)
