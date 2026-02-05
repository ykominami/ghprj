import argparse


class Cli:
    """コマンドライン引数パーサー"""

    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="get list of github projects"
        )
        self.parser.add_argument("-f", action="store_true", help="force download")
        self.args: argparse.Namespace = self.parser.parse_args()

    def get_args(self) -> argparse.Namespace:
        return self.args
