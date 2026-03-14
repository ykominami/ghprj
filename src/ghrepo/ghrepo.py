"""コマンドライン実行ユーティリティ"""

import argparse
import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import cast

from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex
from yklibpy.common.loggerx import Loggerx

from ghrepo.appconfigx import AppConfigx
from ghrepo.clix import Clix
from ghrepo.command_list import CommandList
from ghrepo.command_setup import CommandSetup

type CommandHandler = Callable[[argparse.Namespace], None]


class Ghrepo:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    # s = "hello\nworld\r\nfoo\n"

    @classmethod
    def init_appstore(cls, normalized_user: str | None) -> AppStore:
        Storex.set_file_type_dict(AppConfigx.file_type_dict)

        if normalized_user is None:
            user: str | None = CommandGhUser().run()
            if Util.is_empty(user):
                user = CommandGhUser.DEFAULT_VALUE_USER
                Loggerx.debug(f"user={user}", __name__)

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
    def _set_log_level_by_verbose(cls, verbose: bool) -> None:
        Loggerx._set_log_level(logging.DEBUG if verbose else logging.INFO)

    @classmethod
    def _debug_if_verbose(cls, verbose: bool, data: object) -> None:
        if verbose:
            Loggerx.debug(json.dumps(data, ensure_ascii=False, indent=2), __name__)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = cast(list[str], appsstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appsstore, json_fields, args.user)

        count = command.get_next_snapshot_count()
        new_assoc = command.get_all_repos(args, appsstore, count)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        command.save_snapshot(count, timestamp, new_assoc)

        # 既存の最新DBも更新しておく。
        appsstore.output_db("db", new_assoc)
        cls._debug_if_verbose(args.verbose, new_assoc)

    @classmethod
    def fix_repos(cls, args: argparse.Namespace) -> None:
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = cast(list[str], appsstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appsstore, json_fields, args.user)
        result = command.fix_storage(args.verbose)
        cls._debug_if_verbose(args.verbose, result)


def main() -> None:
    command_dict: dict[str, CommandHandler] = {
        "setup": Ghrepo.setup,
        "list": Ghrepo.list_repos,
        "fix": Ghrepo.fix_repos,
    }
    """CLIエントリポイント"""
    clix = Clix("GitHub Repository list", command_dict)

    args = clix.parse_args()
    cast(CommandHandler, args.func)(args)


def get_user() -> None:
    command = CommandGhUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    Loggerx.debug(normalized_user, __name__)
