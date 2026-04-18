import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml
from yklibpy.command import Command
from yklibpy.common.loggerx import Loggerx
from yklibpy.config.appconfig import AppConfig
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx

type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]


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

    def get_snapshots_store(self) -> Storex:
        """スナップショット作成記録ファイル (`snapshots.yaml`) に対応する `Storex` を返す。"""
        return self._get_store(AppConfigx.BASE_NAME_SNAPSHOTS)

    def get_repos_store(self) -> Storex:
        """`repos.yaml` に対応する `Storex` を返す。"""
        return self._get_store(AppConfigx.BASE_NAME_REPOS)

    def get_snapshots_path(self) -> Path:
        """スナップショット作成記録ファイル (`snapshots.yaml`) の実ファイルパスを返す。"""
        return self.get_snapshots_store().get_path()

    def get_user_dir(self) -> Path:
        """対象ユーザーの保存ルートディレクトリを返す。"""
        return self.get_snapshots_path().parent

    def get_snapshots_dir(self) -> Path:
        """スナップショットトップディレクトリ (`snapshots/`) のパスを返す。"""
        return self.get_user_dir() / AppConfigx.SNAPSHOT_TOP_DIR_NAME

    @staticmethod
    def _coerce_snapshots_assoc(snapshots_assoc: dict[Any, Any]) -> dict[int, str]:
        """スナップショット作成記録ファイルの辞書キーと値を保存用の型へそろえる。"""
        normalized: dict[int, str] = {}
        for key, value in snapshots_assoc.items():
            try:
                id_key = int(key)
            except (TypeError, ValueError):
                continue
            if id_key <= 0:
                continue
            normalized[id_key] = str(value)

        return dict(sorted(normalized.items()))

    def _load_snapshots_assoc(self) -> dict[int, str]:
        """保存済みスナップショット作成記録ファイルを読み込み、正規化して返す。"""
        loaded_value = self.get_snapshots_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return self._coerce_snapshots_assoc(loaded_value)

    def load_latest_assoc(self) -> RepoAssoc:
        """`repos.yaml` を読み込み、辞書として返す。"""
        loaded_value = self.get_repos_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return cast(RepoAssoc, loaded_value)

    def _output_snapshots_assoc(self, snapshots_assoc: dict[int, str]) -> None:
        """スナップショット作成記録ファイルを永続化し、`AppStore` 内の値も同期する。"""
        self.appstore.output_db(
            AppConfigx.BASE_NAME_SNAPSHOTS, cast(dict[str, Any], snapshots_assoc)
        )
        self._set_db_value(AppConfigx.BASE_NAME_SNAPSHOTS, snapshots_assoc)

    def get_next_snapshot_count(self) -> int:
        """既存スナップショットIDの最大値を参照して次回スナップショットIDを返す。"""
        snapshots_assoc = self._load_snapshots_assoc()
        snapshot_ids = self._collect_snapshot_ids(self.get_snapshots_dir())
        max_record_snapshot_id = max(snapshots_assoc.keys(), default=0)
        max_snapshot_id = max(snapshot_ids, default=0)
        return max(max_record_snapshot_id, max_snapshot_id) + 1

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
        self, args: argparse.Namespace, appstore: AppStore, snapshot_id: int
    ) -> RepoAssoc:
        """GitHub CLI で取得した一覧に管理用フィールドを付与して返す。

        Args:
            args: `list` サブコマンドの引数。
            appstore: 設定・DB ファイルアクセスオブジェクト。
            snapshot_id: 今回付与するスナップショットID。

        Returns:
            リポジトリ名をキーとする取得結果。
        """
        assert appstore is self.appstore
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
            item["snapshot-id"] = snapshot_id
            item["valid"] = True
            item["field_1"] = ""
            item["field_2"] = ""
            item["field_3"] = ""
            assoc[name] = item

        return assoc

    def _merge_into_repos(self, new_assoc: RepoAssoc) -> None:
        """`repos.yaml` に新スナップショットの内容をマージ更新する。

        同一リポジトリIDのレコードが存在し内容に差異があれば新しいレコードで上書きする。
        差異がなければ更新しない。
        """
        repos_store = self.get_repos_store()
        loaded = repos_store.load()
        repos_assoc: RepoAssoc = cast(RepoAssoc, loaded) if isinstance(loaded, dict) else {}

        for repo_id, item in new_assoc.items():
            if repo_id not in repos_assoc or repos_assoc[repo_id] != item:
                repos_assoc[repo_id] = item

        repos_store.output(repos_assoc)
        self._set_db_value(AppConfigx.BASE_NAME_REPOS, repos_assoc)

    def save_snapshot(
        self, snapshot_id: int, timestamp: str, assoc: RepoAssoc
    ) -> None:
        """取得結果をスナップショットとして保存し、`snapshots.yaml` と `repos.yaml` も更新する。

        更新順序:
        1. `snapshots/<snapshot-id>/snapshot.yaml` を出力する。
        2. `snapshots.yaml` に `<snapshot-id>: <timestamp>` を反映する。
        3. `repos.yaml` をマージ更新する。
        """
        # 1. snapshots/<snapshot-id>/snapshot.yaml を出力する
        snapshot_dir = self.get_snapshots_dir() / str(snapshot_id)
        snapshot_path = snapshot_dir / "snapshot.yaml"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        with snapshot_path.open("w", encoding="utf-8") as snapshot_file:
            yaml.safe_dump(assoc, snapshot_file, allow_unicode=True, sort_keys=True)

        # 2. snapshots.yaml を更新する
        snapshots_assoc = self._load_snapshots_assoc()
        snapshots_assoc[snapshot_id] = timestamp
        self._output_snapshots_assoc(dict(sorted(snapshots_assoc.items())))

        # 3. repos.yaml をマージ更新する
        self._merge_into_repos(assoc)

    @staticmethod
    def _remove_empty_directories(root_dir: str | Path) -> int:
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

    @staticmethod
    def _collect_snapshot_ids(snapshots_dir: str | Path) -> list[int]:
        """スナップショットトップディレクトリ配下の数値ディレクトリ名を昇順で収集する。

        数値に解釈できないディレクトリ名は対象に含めない。
        """
        snapshot_top_path = Path(snapshots_dir)
        if not snapshot_top_path.exists() or not snapshot_top_path.is_dir():
            return []

        ids: list[int] = []
        for child_path in snapshot_top_path.iterdir():
            if not child_path.is_dir():
                continue
            try:
                snapshot_id = int(child_path.name)
            except ValueError:
                continue
            if snapshot_id > 0:
                ids.append(snapshot_id)

        ids.sort()
        return ids

    @staticmethod
    def _normalize_snapshots_assoc(
        snapshots_assoc: dict[Any, Any],
        snapshot_ids: list[int],
        fallback_timestamp: str,
    ) -> tuple[dict[int, str], bool]:
        """スナップショット作成記録ファイルの内容を数値キー辞書へ正規化し、最大IDに合わせて補正する。

        Args:
            snapshots_assoc: 永続化済みのスナップショットID と日時の対応。
            snapshot_ids: スナップショットトップディレクトリから得た有効なID一覧。
            fallback_timestamp: 最大IDの補完に使う既定日時。

        Returns:
            正規化後の辞書と、入力から内容を変更したかどうか。
        """
        normalized: dict[int, str] = {}
        changed = False

        for key, value in snapshots_assoc.items():
            try:
                id_key = int(key)
            except (TypeError, ValueError):
                changed = True
                continue

            if id_key <= 0:
                changed = True
                continue

            string_value = str(value)
            if not isinstance(key, int) or not isinstance(value, str):
                changed = True
            normalized[id_key] = string_value

        if not snapshot_ids:
            return {}, changed or bool(normalized)

        max_snapshot_id = max(snapshot_ids)
        trimmed = {
            key: value
            for key, value in normalized.items()
            if key <= max_snapshot_id
        }
        if trimmed != normalized:
            changed = True

        if max_snapshot_id not in trimmed:
            latest_timestamp = ""
            if trimmed:
                latest_timestamp = trimmed[max(trimmed)]
            elif normalized:
                latest_timestamp = normalized[max(normalized)]
            trimmed[max_snapshot_id] = latest_timestamp or fallback_timestamp
            changed = True

        sorted_result = dict(sorted(trimmed.items()))
        return sorted_result, changed

    def fix_storage(self, verbose: bool = False) -> dict[str, Any]:
        """保存済みスナップショット構成を点検し、必要な補正結果を返す。

        Returns:
            削除件数、最大スナップショットID、`snapshots.yaml` 更新有無、警告一覧を含む結果辞書。
        """
        warnings: list[str] = []
        user_dir = self.get_user_dir()
        snapshots_dir = self.get_snapshots_dir()

        removed_empty_directories = self._remove_empty_directories(user_dir)
        snapshot_ids = self._collect_snapshot_ids(snapshots_dir)
        if not snapshots_dir.exists():
            warnings.append("スナップショットトップディレクトリが存在しません")

        snapshots_assoc = self._load_snapshots_assoc()
        fallback_timestamp = ""
        if snapshots_assoc:
            fallback_timestamp = snapshots_assoc[max(snapshots_assoc)]
        if fallback_timestamp == "":
            fallback_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

        normalized_assoc, snapshots_updated = self._normalize_snapshots_assoc(
            snapshots_assoc, snapshot_ids, fallback_timestamp
        )
        snapshots_path = self.get_snapshots_path()
        snapshots_exists_before = snapshots_path.exists()
        if snapshots_updated or not snapshots_exists_before:
            self._output_snapshots_assoc(normalized_assoc)

        result: dict[str, Any] = {
            "removed_empty_directories": removed_empty_directories,
            "max_snapshot_id": max(snapshot_ids, default=None),
            "snapshots_updated": snapshots_updated or not snapshots_exists_before,
            "warnings": warnings,
        }
        if verbose and warnings:
            for warning in warnings:
                Loggerx.warning(warning, __name__)

        return result
