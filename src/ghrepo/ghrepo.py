"""コマンドライン実行ユーティリティ"""

import argparse
import json
from datetime import datetime

from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx
from ghrepo.clix import Clix
from ghrepo.command_list import CommandList
from ghrepo.command_setup import CommandSetup


class Ghrepo:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    # s = "hello\nworld\r\nfoo\n"

    @classmethod
    def init_appstore(cls, normalized_user: str | None) -> AppStore:
        Storex.set_file_type_dict(AppConfigx.file_type_dict)

        # print(f'A Ghrepo init_appstore normalized_user={normalized_user}')
        if normalized_user is None:
            user = CommandGhUser().run()
            if Util.is_empty(user):
                user = CommandGhUser.DEFAULT_VALUE_USER
                print(f"user={user}")

            normalized_user = Util.normalize_string(user)

        appstore = AppStore("ghrepo", AppConfigx.file_assoc, normalized_user)
        appstore.prepare_config_file_and_db_file()
        return appstore

    @classmethod
    def setup(cls, args: argparse.Namespace) -> None:
        appsstore = cls.init_appstore(args.user)
        command = CommandSetup(appsstore)
        command.run(AppConfigx.key, AppConfigx.default_json_fields)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = appsstore.get_from_config("config", AppConfigx.key)
        command = CommandList(appsstore, json_fields, args.user)

        count = command.get_next_snapshot_count()
        new_assoc = command.get_all_repos(args, appsstore, count)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        command.save_snapshot(count, timestamp, new_assoc)

        # 既存の最新DBも更新しておく。
        appsstore.output_db("db", new_assoc)
        if args.verbose:
            print(json.dumps(new_assoc, ensure_ascii=False, indent=2))

    @classmethod
    def fix_repos(cls, args: argparse.Namespace) -> None:
        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = appsstore.get_from_config("config", AppConfigx.key)
        command = CommandList(appsstore, json_fields, args.user)
        result = command.fix_storage(args.verbose)
        if args.verbose:
            print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    command_dict = {
        "setup": Ghrepo.setup,
        "list": Ghrepo.list_repos,
        "fix": Ghrepo.fix_repos,
    }
    """CLIエントリポイント"""
    clix = Clix("GitHub Repository list", command_dict)

    args = clix.parse_args()
    args.func(args)


def get_user() -> None:
    command = CommandGhUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    print(normalized_user)

