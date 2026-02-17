import json
from pathlib import Path
from typing import Any, Optional, cast

"""コマンドライン実行ユーティリティ"""

from ghprj.clix import Clix
from ghprj.appconfigx import AppConfigx
from ghprj.command_setup import CommandSetup
from ghprj.command_repo import CommandRepo
from yklibpy.db.storex import Storex
from yklibpy.db.appstore import AppStore


class Ghprj:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    @classmethod
    def init_appsstore(cls) -> AppStore:
        Storex.set_file_type_dict(AppConfigx.file_type_dict)
        appstore = AppStore("ghprj", AppConfigx.file_assoc)
        appstore.prepare_config_file_and_db_file()
        return appstore

    @classmethod
    def setup(cls, args: argparse.Namespace) -> None:
        # print(args)
        appstore = Ghprj.init_appsstore()
        command = CommandSetup(appstore)
        command.run(AppConfigx.key, AppConfigx.default_json_fields)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        # print(args)
        appstore = Ghprj.init_appsstore()
        appstore.load_file()
        json_fields = appstore.get_from_config("config", AppConfigx.key)
        command = CommandRepo(appstore, json_fields)

        fetch_assoc = appstore.get_assoc_from_db("fetch")
        [count, fetch_assoc] = command.get_next_count(fetch_assoc)
        if count == 1 or args.f:
            appstore.output_db("fetch", fetch_assoc)
            new_assoc = command.get_all_repos(args, appstore, count)
            appstore.output_db("db", new_assoc)

        if args.v:
            appstore.show_db("db")
 

def main() -> None:
    command_dict = {'setup': Ghprj.setup, 'list': Ghprj.list_repos}
    """CLIエントリポイント"""
    clix = Clix('GitHub Repository list', command_dict)

    args = clix.parse_args()
    args.func(args)

def get_user() -> None:
    command = CommandUser()
    user = command.run()
    print(user)
