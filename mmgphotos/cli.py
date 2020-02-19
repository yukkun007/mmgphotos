import argparse
import logging
from mmgphotos.google_photos import GooglePhotos


def main():
    parser = argparse.ArgumentParser(
        description="""
    Google Photos の情報を取得します。
    """
    )

    # parser.add_argument("-t", "--test", help="何か文字列を指定")
    parser.add_argument("-m", "--mode", help="モードを指定します", choices=["download", "get"])
    parser.add_argument("-d", "--debug", help="デバッグログ出力をONにします", action="store_true")

    args = parser.parse_args()

    # log設定
    formatter = "%(asctime)s : %(levelname)s : %(message)s"
    if args.debug:
        # ログレベルを DEBUG に変更
        logging.basicConfig(level=logging.DEBUG, format=formatter)
    else:
        logging.basicConfig(format=formatter)

    gphotos = GooglePhotos()
    if args.mode == "download":
        gphotos.download_video()
    elif args.mode == "get":
        gphotos.get_album_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
