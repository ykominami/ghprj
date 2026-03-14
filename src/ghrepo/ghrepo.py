"""コマンドライン実行ユーティリティ"""

import argparse
import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import cast

from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.loggerx import Loggerx
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx
from ghrepo.clix import Clix
from ghrepo.command_list import CommandList
from ghrepo.command_setup import CommandSetup

type CommandHandler = Callable[[argparse.Namespace], None]


class Ghrepo:
    """`ghrepo` の主要 CLI 処理を束ねる統括クラス。"""

    # s = "hello\nworld\r\nfoo\n"

    @classmethod
    def init_appstore(cls, normalized_user: str | None) -> AppStore:
        """対象ユーザーに対応する `AppStore` を準備して返す。

        Args:
            normalized_user: 正規化済み GitHub ユーザー名。`None` の場合は実行環境から補完する。

        Returns:
            設定ファイルと DB ファイルの準備が済んだ `AppStore`。
        """
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
        """設定ファイルと保存先 DB の初期化を実行する。"""
        appsstore = cls.init_appstore(args.user)
        command = CommandSetup(appsstore)
        command.run(AppConfigx.key, AppConfigx.default_json_fields)

    @classmethod
    def _set_log_level_by_verbose(cls, verbose: bool) -> None:
        """`verbose` の値に応じてログレベルを切り替える。"""
        Loggerx.set_log_level(logging.DEBUG if verbose else logging.INFO)

    @classmethod
    def _debug_if_verbose(cls, verbose: bool, data: object) -> None:
        """`verbose` が有効なときだけ整形済み JSON をデバッグ出力する。"""
        if verbose:
            Loggerx.debug(json.dumps(data, ensure_ascii=False, indent=2), __name__)

    @classmethod
    def list_repos(cls, args: argparse.Namespace) -> None:
        """GitHub リポジトリ一覧を取得し、最新 DB とスナップショットを更新する。"""
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = cast(list[str], appsstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appsstore, json_fields, args.user)
        should_fetch = args.force or not command.get_fetch_path().exists()

        if should_fetch:
            count = command.get_next_snapshot_count()
            new_assoc = command.get_all_repos(args, appsstore, count)
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            command.save_snapshot(count, timestamp, new_assoc)

            # 最新DBはレコード単位で差分反映する（countのみ差分は更新しない）。
            latest_db_path = command.get_db_store().get_path()
            if not latest_db_path.exists():
                merged_assoc = new_assoc
            else:
                latest_assoc, loaded_ok = command.load_latest_assoc_with_status()
                if not loaded_ok:
                    Loggerx.warning(
                        "latest repository db is invalid; fallback to snapshot output",
                        __name__,
                    )
                    merged_assoc = new_assoc
                else:
                    merged_assoc = command.merge_latest_assoc_by_record(
                        latest_assoc, new_assoc
                    )

            appsstore.output_db("db", merged_assoc)
            cls._debug_if_verbose(args.verbose, merged_assoc)
            return

        latest_db_path = command.get_db_store().get_path()
        if not latest_db_path.exists():
            raise FileNotFoundError(f"latest repository db does not exist: {latest_db_path}")

        latest_assoc = command.load_latest_assoc()
        cls._debug_if_verbose(args.verbose, latest_assoc)

    @classmethod
    def fix_repos(cls, args: argparse.Namespace) -> None:
        """保存済みスナップショットと `fetch` 情報の整合性を補正する。"""
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appsstore = cls.init_appstore(normalized_user)
        appsstore.load_file_all()
        json_fields = cast(list[str], appsstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appsstore, json_fields, args.user)
        result = command.fix_storage(args.verbose)
        cls._debug_if_verbose(args.verbose, result)


def main() -> None:
    """CLI 引数を解析し、選択されたサブコマンドを実行する。"""
    command_dict: dict[str, CommandHandler] = {
        "setup": Ghrepo.setup,
        "list": Ghrepo.list_repos,
        "fix": Ghrepo.fix_repos,
    }
    clix = Clix("GitHub Repository list", command_dict)

    args = clix.parse_args()
    cast(CommandHandler, args.func)(args)


def get_user() -> None:
    """現在の GitHub ユーザー名を正規化してログ出力する。"""
    command = CommandGhUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    Loggerx.debug(normalized_user, __name__)
