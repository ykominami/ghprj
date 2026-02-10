import argparse
from typing import Any

from ghprj.appconfig import AppConfig
from ghprj.appstore import AppStore
from ghprj.storex import Storex
from ghprj.command_user import CommandUser


class Cli:
    def __init__(self, appstore: AppStore, key: str) -> None:
        self.appstore = appstore

        self.default_json_fields = []

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

    def load_file(self):
        self.appstore.load_file()

    def get_from_config(self, base_name:str, key: str) -> Any:
        return self.appstore.get_from_config(base_name, key)

    def get_from_db(self, base_name: str, key: str) -> Any:
        return self.appstore.get_from_db(base_name, key)

    def setup(self, key: str, default_json_fields: list[str]) -> None:
        user = CommandUser().get_user()
        data = {key: default_json_fields, "USER": user}
        self.appstore.output_config("config", data)
        self.appstore.output_db("db", "")
        self.appstore.output_db("fetch", "")

    def get_appstore(self) -> AppStore:
        return self.appstore
