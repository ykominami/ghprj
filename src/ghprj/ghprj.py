import json
from pathlib import Path
from typing import Any, Optional, cast

"""コマンドライン実行ユーティリティ"""
from ghprj.appconfig import AppConfig
from ghprj.storex import Storex

from ghprj.cli import Cli
from ghprj.command_repo import CommandRepo
from ghprj.command_user import CommandUser
from ghprj.command_setup import CommandSetup
from ghprj.appstore import AppStore


class Ghprj:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    def __init__(self) -> None:
        """Ghprjインスタンスを初期化する"""
        pass

    def get_all_repos(self) -> None:
        """CLIエントリポイント"""
        Storex.set_file_type_dict(AppConfig.file_type_dict)

        appstore = AppStore("ghprj", AppConfig.file_assoc)
        appstore.prepare_config_file_and_db_file()

        cli = Cli()
        args = cli.get_args()

        if args.setup:
            command = CommandSetup(appstore)
            command.run(AppConfig.key, AppConfig.default_json_fields)
            return

        appstore.load_file()
        json_fields = appstore.get_from_config("config", AppConfig.key)
        command = CommandRepo(appstore, json_fields)

        fetch_assoc = appstore.get_assoc_from_db("fetch")
        [count, fetch_assoc] = command.get_next_count(fetch_assoc)
        if count == 1 or args.f:
            appstore.output_db("fetch", fetch_assoc)
            new_assoc = command.get_all_repos(args, appstore, count)
            appstore.output_db("db", new_assoc)

def main() -> None:
    ghprj = Ghprj()
    ghprj.get_all_repos()

def get_user() -> None:
    command = CommandUser()
    user = command.run()
    print(user)
