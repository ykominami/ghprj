
"""コマンドライン実行ユーティリティ"""

import argparse

from yklibpy.command.fetchcount import FetchCount
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx
from ghrepo.clix import Clix
from ghrepo.command_list import CommandList
from ghrepo.command_setup import CommandSetup
from ghrepo.command_user import CommandUser


class Ghrepo:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    # s = "hello\nworld\r\nfoo\n"

    @classmethod
    def init_appstore(cls, normalized_user: str | None) -> AppStore:
        Storex.set_file_type_dict(AppConfigx.file_type_dict)

        # print(f'A Ghrepo init_appstore normalized_user={normalized_user}')
        if normalized_user is None:
            user = CommandUser().run()
            normalized_user = Util().normalize_string(user)
            # rint(f'B Ghrepo init_appstore user={normalized_user}')

        # print(f'C Ghrepo init_appstore user={normalized_user}')

        appstore = AppStore("ghrepo", AppConfigx.file_assoc, normalized_user)
        appstore.prepare_config_file_and_db_file()
        return appstore

    @classmethod
    def setup(cls, args: argparse.Namespace) -> None:
        normalized_user = Util().normalize_string(args.user)
        if normalized_user is None:
            normalized_user = CommandUser().run()
            normalized_user = Util().normalize_string(normalized_user)
            # print(f'D Ghrepo setup normalized_user={normalized_user}')

        appsstore = cls.init_appstore(normalized_user)
        command = CommandSetup(appsstore)
        command.run(AppConfigx.key, AppConfigx.default_json_fields)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        normalized_user = Util().normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = appsstore.get_from_config("config", AppConfigx.key)
        command = CommandList(appsstore, json_fields, args.user)

        fetch_count = FetchCount(True, False, appsstore)
        count = fetch_count.get()
        if count == 1 or args.f:
            fetch_count.output_db()
            new_assoc = command.get_all_repos(args, appsstore, count)
            appsstore.output_db("db", new_assoc)
        if args.v:
            appsstore.show_db("db")
 

def main() -> None:
    command_dict = {'setup': Ghrepo.setup, 'list': Ghrepo.list_repos}
    """CLIエントリポイント"""
    clix = Clix('GitHub Repository list', command_dict)

    args = clix.parse_args()
    args.func(args)

def get_user() -> None:
    command = CommandUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    print(normalized_user)

