"""コマンドライン実行ユーティリティ"""

import argparse
import json
import logging
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import cast

from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.loggerx import Loggerx
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx
from ghrepo.clix import Clix
from ghrepo.command_list import CommandList
from ghrepo.command_search import CommandSearch
from ghrepo.command_setup import CommandSetup

type CommandHandler = Callable[[argparse.Namespace], None]


class Ghrepo:
    """`ghrepo` の主要 CLI 処理を束ねる統括クラス。"""

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
        appstore = cls.init_appstore(args.user)
        command = CommandSetup(appstore)
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
        appstore = cls.init_appstore(normalized_user)
        appstore.load_file_all()
        json_fields = cast(list[str], appstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appstore, json_fields, args.user)
        should_fetch = args.force or not command.get_snapshots_path().exists()

        if should_fetch:
            snapshot_id = command.get_next_snapshot_count()
            new_assoc = command.get_all_repos(args, appstore, snapshot_id)
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            command.save_snapshot(snapshot_id, timestamp, new_assoc)

            cls._debug_if_verbose(args.verbose, new_assoc)
            Path(args.output).write_text(
                json.dumps(new_assoc, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return

        repos_file_path = command.get_repos_store().get_path()
        if not repos_file_path.exists():
            raise FileNotFoundError(f"リポジトリ一覧ファイルが存在しません: {repos_file_path}")

        latest_assoc = command.load_latest_assoc()
        cls._debug_if_verbose(args.verbose, latest_assoc)
        Path(args.output).write_text(
            json.dumps(latest_assoc, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def fix_repos(cls, args: argparse.Namespace) -> None:
        """空ディレクトリ削除とスナップショット作成記録ファイルの整合性補正を実行する。`repos.yaml` は変更しない。"""
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appstore = cls.init_appstore(normalized_user)
        appstore.load_file_all()
        json_fields = cast(list[str], appstore.get_from_config("config", AppConfigx.key))
        command = CommandList(appstore, json_fields, args.user)
        result = command.fix_storage(args.verbose)
        cls._debug_if_verbose(args.verbose, result)

    @classmethod
    def search_repos(cls, args: argparse.Namespace) -> None:
        """保存済みスナップショットから条件一致するリポジトリを検索する。"""
        cls._set_log_level_by_verbose(args.verbose)

        normalized_user = Util.normalize_string(args.user)
        appstore = cls.init_appstore(normalized_user)
        appstore.load_file_all()
        command = CommandSearch(appstore, args.user)
        _result = command.search_repos(args.search_name, args.name, args.user)
        if args.all:
            print(json.dumps(_result, ensure_ascii=False))
        else:
            _names = [item["name"] for item in _result]
            print(json.dumps(_names, ensure_ascii=True))


def main() -> None:
    """CLI 引数を解析し、選択されたサブコマンドを実行する。"""
    command_dict: dict[str, CommandHandler] = {
        "setup": Ghrepo.setup,
        "list": Ghrepo.list_repos,
        "fix": Ghrepo.fix_repos,
        "search": Ghrepo.search_repos,
    }
    clix = Clix("GitHub Repository list", command_dict)

    args = clix.parse_args()
    cast(CommandHandler, args.func)(args)


def get_user() -> None:
    """現在の GitHub ユーザー名を正規化してログ出力する。"""
    command = CommandGhUser()
    user = command.run()
    normalized_user = Util.normalize_string(user)
    if Util.is_empty(normalized_user):
        normalized_user = CommandGhUser.DEFAULT_VALUE_USER
    Loggerx.debug(cast(str, normalized_user), __name__)
