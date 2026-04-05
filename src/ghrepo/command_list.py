import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml
from yklibpy.command import Command
from yklibpy.config.appconfig import AppConfig
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex
from yklibpy.common.loggerx import Loggerx

type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]


def remove_empty_directories(root_dir: str | Path) -> int:
    """指定ディレクトリ配下の空ディレクトリを末端から削除する。"""
    root_path = Path(root_dir)
    if not root_path.exists():
        return 0

    removed_count = 0
    directory_paths = sorted(
        (path for path in root_path.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory_path in directory_paths:
        try:
            if not any(directory_path.iterdir()):
                directory_path.rmdir()
                removed_count += 1
        except OSError:
            continue

    return removed_count


def collect_repolist_counts(repolist_dir: str | Path) -> list[int]:
    """`repolist` 配下の数値ディレクトリ名を昇順で収集する。"""
    repolist_path = Path(repolist_dir)
    if not repolist_path.exists() or not repolist_path.is_dir():
        return []

    counts: list[int] = []
    for child_path in repolist_path.iterdir():
        if not child_path.is_dir():
            continue
        try:
            count = int(child_path.name)
        except ValueError:
            continue
        if count > 0:
            counts.append(count)

    counts.sort()
    return counts


def normalize_fetch_assoc(
    fetch_assoc: dict[Any, Any],
    repolist_counts: list[int],
    fallback_timestamp: str,
) -> tuple[dict[int, str], bool]:
    """`fetch` 情報を数値キー辞書へ正規化し、最新件数に合わせて補正する。

    Args:
        fetch_assoc: 永続化済みの取得回数と日時の対応。
        repolist_counts: `repolist` ディレクトリから得た有効な件数一覧。
        fallback_timestamp: 最新件数の補完に使う既定日時。

    Returns:
        正規化後の `fetch` 辞書と、入力から内容を変更したかどうか。
    """
    normalized_fetch: dict[int, str] = {}
    changed = False

    for key, value in fetch_assoc.items():
        try:
            count_key = int(key)
        except (TypeError, ValueError):
            changed = True
            continue

        if count_key <= 0:
            changed = True
            continue

        string_value = str(value)
        if not isinstance(key, int) or not isinstance(value, str):
            changed = True
        normalized_fetch[count_key] = string_value

    if not repolist_counts:
        return {}, changed or bool(normalized_fetch)

    max_repolist_count = max(repolist_counts)
    trimmed_fetch = {
        key: value
        for key, value in normalized_fetch.items()
        if key <= max_repolist_count
    }
    if trimmed_fetch != normalized_fetch:
        changed = True

    if max_repolist_count not in trimmed_fetch:
        latest_timestamp = ""
        if trimmed_fetch:
            latest_timestamp = trimmed_fetch[max(trimmed_fetch)]
        elif normalized_fetch:
            latest_timestamp = normalized_fetch[max(normalized_fetch)]
        trimmed_fetch[max_repolist_count] = latest_timestamp or fallback_timestamp
        changed = True

    sorted_fetch = dict(sorted(trimmed_fetch.items()))
    return sorted_fetch, changed


class CommandList(Command):
    """リポジトリ一覧の取得、保存、補正を担当するコマンド群。"""

    def __init__(self, appstore: AppStore, json_fields: list[str], user: str | None) -> None:
        """保存先と取得対象ユーザーに関する実行文脈を保持する。"""
        self.appstore: AppStore = appstore
        self.json_fields: list[str] = json_fields
        self.user: str | None = user
        self.config_user: str = cast(str, self.appstore.get_from_config("config", "USER"))

    def _get_store(self, base_name: str) -> Storex:
        """ユーザー別設定を考慮して対象 `Storex` を返す。"""
        path_assoc = self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.PATH]
        if self.appstore.user is None:
            return cast(Storex, path_assoc)
        return cast(Storex, path_assoc[self.appstore.user])

    def _set_db_value(self, base_name: str, data: dict[Any, Any]) -> None:
        """`AppStore` 内のキャッシュ済み DB 値を更新する。"""
        if self.appstore.user is None:
            self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.VALUE] = data
            return

        self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.VALUE][
            self.appstore.user
        ] = data

    def get_fetch_store(self) -> Storex:
        """`fetch` DB に対応する `Storex` を返す。"""
        return self._get_store(AppConfig.BASE_NAME_FETCH)

    def get_db_store(self) -> Storex:
        """最新リポジトリ DB に対応する `Storex` を返す。"""
        return self._get_store("db")

    def get_fetch_path(self) -> Path:
        """`fetch` DB の実ファイルパスを返す。"""
        return self.get_fetch_store().get_path()

    def get_user_dir(self) -> Path:
        """対象ユーザーの保存ルートディレクトリを返す。"""
        return self.get_fetch_path().parent

    def get_repolist_dir(self) -> Path:
        """スナップショット保存先の `repolist` ディレクトリを返す。"""
        return self.get_user_dir() / "repolist"

    @staticmethod
    def coerce_fetch_assoc(fetch_assoc: dict[Any, Any]) -> dict[int, str]:
        """`fetch` 辞書のキーと値を保存用の型へそろえる。"""
        normalized_fetch: dict[int, str] = {}
        for key, value in fetch_assoc.items():
            try:
                count_key = int(key)
            except (TypeError, ValueError):
                continue
            if count_key <= 0:
                continue
            normalized_fetch[count_key] = str(value)

        return dict(sorted(normalized_fetch.items()))

    def load_fetch_assoc(self) -> dict[int, str]:
        """保存済み `fetch` 情報を読み込み、正規化して返す。"""
        loaded_value = self.get_fetch_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return self.coerce_fetch_assoc(loaded_value)

    def load_latest_assoc(self) -> RepoAssoc:
        """最新リポジトリ DB を読み込み、辞書として返す。"""
        loaded_value = self.get_db_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return cast(RepoAssoc, loaded_value)

    def output_fetch_assoc(self, fetch_assoc: dict[int, str]) -> None:
        """`fetch` 辞書を永続化し、`AppStore` 内の値も同期する。"""
        self.appstore.output_db(
            AppConfig.BASE_NAME_FETCH, cast(dict[str, Any], fetch_assoc)
        )
        self._set_db_value(AppConfig.BASE_NAME_FETCH, fetch_assoc)

    def get_next_snapshot_count(self) -> int:
        """既存保存件数を参照して次回スナップショット番号を返す。"""
        fetch_assoc = self.load_fetch_assoc()
        repolist_counts = collect_repolist_counts(self.get_repolist_dir())
        max_fetch_count = max(fetch_assoc.keys(), default=0)
        max_repolist_count = max(repolist_counts, default=0)
        return max(max_fetch_count, max_repolist_count) + 1

    def get_command_for_repository(self, args: argparse.Namespace) -> str:
        """CLI 引数と設定値から `gh repo list` コマンド文字列を組み立てる。"""
        target_user = self.config_user
        if args.user is not None and args.user != "":
            target_user = args.user

        limit_value = 400 if args.limit is None else args.limit
        options = [f"--limit {limit_value}"]

        if args.json is None:
            json_fields = list(self.json_fields)
        else:
            # `gh` CLI の `--json` はカンマ区切りのフィールド列を想定する。
            # ユーザ指定が `visibility` を含まない場合でも、必ず `visibility` を追加する。
            json_fields = [field.strip() for field in args.json.split(",") if field.strip()]

        # `visibility` の強制追加（重複は順序維持で除去）
        if "visibility" not in json_fields:
            json_fields.append("visibility")
        seen_fields: set[str] = set()
        normalized_fields: list[str] = []
        for field in json_fields:
            if field in seen_fields:
                continue
            seen_fields.add(field)
            normalized_fields.append(field)

        json_value = ",".join(normalized_fields)
        options.append(f"--json {json_value}")

        command_parts = ["gh repo list"]
        if target_user != "":
            command_parts.append(target_user)
        command_parts.append(" ".join(options))

        return " ".join(command_parts)

    @staticmethod
    def array_to_dict(array: list[RepoItem], key: str) -> RepoAssoc:
        """リポジトリ配列を指定キー基準の連想配列へ変換する。"""
        return {cast(str, item[key]): item for item in array}

    def get_all_repos(
        self, args: argparse.Namespace, appstore: AppStore, count: int
    ) -> RepoAssoc:
        """GitHub CLI で取得した一覧に管理用フィールドを付与して返す。

        Args:
            args: `list` サブコマンドの引数。
            appstore: 互換性維持のため受け取る未使用引数。
            count: 今回付与する取得回数。

        Returns:
            リポジトリ名をキーとする取得結果。
        """
        del appstore

        command_line = self.get_command_for_repository(args)
        json_str = self.run_command_simple(command_line)
        try:
            json_array = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise ValueError("gh repo list returned invalid JSON output") from exc

        if not isinstance(json_array, list):
            raise ValueError("gh repo list must return a JSON array")
        if any(
            not isinstance(item, dict) or "name" not in item or "visibility" not in item
            for item in json_array
        ):
            raise ValueError(
                "gh repo list output must include repository names and visibility"
            )

        allowed_visibility = {"public", "internal", "private"}
        for item in json_array:
            visibility_value = item["visibility"]
            if not isinstance(visibility_value, str):
                raise ValueError(
                    "gh repo list output has invalid visibility value: "
                    f"{visibility_value!r}"
                )
            normalized = visibility_value.lower()
            if normalized not in allowed_visibility:
                raise ValueError(
                    "gh repo list output has invalid visibility value: "
                    f"{visibility_value!r}"
                )
            # `gh` は PUBLIC 等の大文字で返すことがある。保存は public/internal/private に統一する。
            item["visibility"] = normalized

        assoc = self.array_to_dict(json_array, "name")
        for name, item in list(assoc.items()):
            item["count"] = count
            item["valid"] = True
            item["field_1"] = ""
            item["field_2"] = ""
            item["field_3"] = ""
            assoc[name] = item

        return assoc

    def save_snapshot(
        self, count: int, timestamp: str, assoc: RepoAssoc
    ) -> None:
        """取得結果を件数別スナップショットとして保存し、`fetch` も更新する。"""
        snapshot_dir = self.get_repolist_dir() / str(count)
        snapshot_path = snapshot_dir / "db.yaml"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        with snapshot_path.open("w", encoding="utf-8") as snapshot_file:
            yaml.safe_dump(assoc, snapshot_file, allow_unicode=True, sort_keys=True)

        fetch_assoc = self.load_fetch_assoc()
        fetch_assoc[count] = timestamp
        self.output_fetch_assoc(dict(sorted(fetch_assoc.items())))

    def fix_storage(self, verbose: bool = False) -> dict[str, Any]:
        """保存済みスナップショット構成を点検し、必要な補正結果を返す。

        Returns:
            削除件数、最新件数、`fetch` 更新有無、警告一覧を含む結果辞書。
        """
        warnings: list[str] = []
        user_dir = self.get_user_dir()
        repolist_dir = self.get_repolist_dir()

        removed_empty_directories = remove_empty_directories(user_dir)
        repolist_counts = collect_repolist_counts(repolist_dir)
        if not repolist_dir.exists():
            warnings.append("repolist directory does not exist")

        fetch_assoc = self.load_fetch_assoc()
        fallback_timestamp = ""
        if fetch_assoc:
            fallback_timestamp = fetch_assoc[max(fetch_assoc)]
        if fallback_timestamp == "":
            fallback_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

        normalized_fetch_assoc, fetch_updated = normalize_fetch_assoc(
            fetch_assoc, repolist_counts, fallback_timestamp
        )
        fetch_path = self.get_fetch_path()
        fetch_exists_before = fetch_path.exists()
        if fetch_updated or not fetch_exists_before:
            self.output_fetch_assoc(normalized_fetch_assoc)

        result = {
            "removed_empty_directories": removed_empty_directories,
            "max_repolist_count": max(repolist_counts, default=None),
            "fetch_updated": fetch_updated or not fetch_exists_before,
            "warnings": warnings,
        }
        if verbose and warnings:
            for warning in warnings:
                Loggerx.warning(warning, __name__)

        return result
