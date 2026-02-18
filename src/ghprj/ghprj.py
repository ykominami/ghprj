
"""コマンドライン実行ユーティリティ"""

import argparse

from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghprj.appconfigx import AppConfigx
from ghprj.clix import Clix
from ghprj.command_list import CommandList
from ghprj.command_setup import CommandSetup
from ghprj.command_user import CommandUser


class Ghprj:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    # s = "hello\nworld\r\nfoo\n"

    @classmethod
    def init_appstore(cls, normalized_user: str | None) -> AppStore:
        Storex.set_file_type_dict(AppConfigx.file_type_dict)

        # print(f'A Ghprj init_appstore normalized_user={normalized_user}')
        if normalized_user is None:
            user = CommandUser().run()
            normalized_user = Util().normalize_string(user)
            # rint(f'B Ghprj init_appstore user={normalized_user}')

        # print(f'C Ghprj init_appstore user={normalized_user}')

        appstore = AppStore("ghprj", AppConfigx.file_assoc, normalized_user)  # type: ignore[arg-type]
        appstore.prepare_config_file_and_db_file()  # type: ignore[no-untyped-call]
        return appstore

    @classmethod
    def setup(cls, args: argparse.Namespace) -> None:
        normalized_user = Util().normalize_string(args.user)
        if normalized_user is None:
            normalized_user = CommandUser().run()
            normalized_user = Util().normalize_string(normalized_user)
            # print(f'D Ghprj setup normalized_user={normalized_user}')

        appsstore = cls.init_appstore(normalized_user)
        command = CommandSetup(appsstore)
        command.run(AppConfigx.key, AppConfigx.default_json_fields)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        normalized_user = Util().normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file()  # type: ignore[no-untyped-call]
        json_fields = appsstore.get_from_config("config", AppConfigx.key)
        command = CommandList(appsstore, json_fields, args.user)

        fetch_assoc = appsstore.get_assoc_from_db("fetch")
        [count, fetch_assoc] = command.get_next_count(fetch_assoc)
        if count == 1 or args.f:
            appsstore.output_db("fetch", fetch_assoc)  # type: ignore[arg-type]
            new_assoc = command.get_all_repos(args, appsstore, count)
            appsstore.output_db("db", new_assoc)
        if args.v:
            appsstore.show_db("db")
 

def main() -> None:
    command_dict = {'setup': Ghprj.setup, 'list': Ghprj.list_repos}
    """CLIエントリポイント"""
    clix = Clix('GitHub Repository list', command_dict)

    args = clix.parse_args()
    args.func(args)

def get_user() -> None:
    command = CommandUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    print(normalized_user)

