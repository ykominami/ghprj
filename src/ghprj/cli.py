import argparse
from typing import Any

from ghprj.appstore import AppStore

class Cli:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="get list of github projeccts"
        )
        self.parser.add_argument(
            "--setup", action="store_true", help="setup for config file"
        )
        self.parser.add_argument("-f", action="store_true", help="force download")
        self.parser.add_argument("-v", action="store_true", help="verbose")
        self.parser.add_argument("--user", help="GitHub user name")
        self.parser.add_argument("--limit", type=int, help="limit the number of repos")
        self.parser.add_argument("--json", type=str, help="json output")
        default_output_file = "repos.json"
        self.parser.add_argument(
            "--output", default=default_output_file, help="Output file name"
        )
        self.args = self.parser.parse_args()

    def get_args(self) -> argparse.Namespace:
        return self.args
