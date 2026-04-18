from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, cast

import yaml
from yklibpy.command import Command
from yklibpy.config.appconfig import AppConfig
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.appconfigx import AppConfigx

type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]

class CommandSearch(Command):
    """保存済みスナップショットを検索するコマンド。"""

    SEARCH_KINDS: ClassVar[frozenset[str]] = frozenset(
        {"public", "private", "both", "internal", "latest10"}
    )

    def __init__(self, appstore: AppStore, user: str | None) -> None:
        self.appstore: AppStore = appstore
        self.user: str | None = user
        self.config_user: str = cast(str, self.appstore.get_from_config("config", "USER"))

    def _get_store(self, base_name: str) -> Storex:
        """ユーザー別設定を考慮して対象 `Storex` を返す。"""
        path_assoc = self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.PATH]
        if self.appstore.user is None:
            return cast(Storex, path_assoc)
        return cast(Storex, path_assoc[self.appstore.user])

    def get_snapshots_record_path(self) -> Path:
        """スナップショット作成記録ファイル (`snapshots.yaml`) の実ファイルパスを返す。"""
        return self._get_store(AppConfigx.BASE_NAME_SNAPSHOTS).get_path()

    def get_user_dir(self) -> Path:
        """対象ユーザーの保存ルートディレクトリを返す。"""
        return self.get_snapshots_record_path().parent

    def get_snapshot_top_dir(self) -> Path:
        """スナップショットトップディレクトリ (`snapshots/`) のパスを返す。"""
        return self.get_user_dir() / AppConfigx.SNAPSHOT_TOP_DIR_NAME

    @staticmethod
    def _collect_snapshot_ids(snapshot_top_dir: str | Path) -> list[int]:
        """スナップショットトップディレクトリ配下の数値ディレクトリ名を昇順で収集する。"""
        snapshot_top_path = Path(snapshot_top_dir)
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

    def _load_latest_snapshot_assoc(self) -> RepoAssoc:
        """最新リポジトリ一覧スナップショットファイルを読み込んで返す。"""
        snapshot_top_dir = self.get_snapshot_top_dir()
        snapshot_ids = self._collect_snapshot_ids(snapshot_top_dir)
        if not snapshot_ids:
            raise FileNotFoundError(f"スナップショットトップディレクトリ配下にスナップショットが存在しません: {snapshot_top_dir}")

        latest_id = max(snapshot_ids)
        snapshot_path = snapshot_top_dir / str(latest_id) / "snapshot.yaml"
        if not snapshot_path.exists():
            raise FileNotFoundError(f"リポジトリ一覧スナップショットファイルが存在しません: {snapshot_path}")

        with snapshot_path.open(encoding="utf-8") as snapshot_file:
            loaded_value = yaml.safe_load(snapshot_file)
        if not isinstance(loaded_value, dict):
            raise ValueError(f"リポジトリ一覧スナップショットファイルの形式が不正です: {snapshot_path}")

        assoc: RepoAssoc = {}
        for key, value in loaded_value.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            assoc[key] = cast(RepoItem, value)
        return assoc

    @staticmethod
    def _filter_by_visibility(assoc: RepoAssoc, visibility: str) -> list[RepoItem]:
        """`visibility` が一致するレコードを返す。"""
        if visibility == "both":
            normalized_visibility = ["public", "private"]
        else:
            normalized_visibility = [visibility.lower()]

        return [
            item
            for item in assoc.values()
            if isinstance(item.get("visibility"), str)
            and cast(str, item["visibility"]).lower() in normalized_visibility
        ]

    @staticmethod
    def _parse_created_at(value: object) -> datetime | None:
        """`createdAt` 値を `datetime` に変換する。"""
        if not isinstance(value, str) or value == "":
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _take_latest_n_by_created_at(self, assoc: RepoAssoc, n: int) -> list[RepoItem]:
        """`createdAt` 降順で上位 `n` 件を返す。"""
        items = list(assoc.values())
        sorted_items = sorted(
            items,
            key=lambda item: (
                self._parse_created_at(item.get("createdAt")) is None,
                -(cast(datetime, self._parse_created_at(item.get("createdAt"))).timestamp())
                if self._parse_created_at(item.get("createdAt")) is not None
                else 0.0,
                str(item.get("name", "")),
            ),
        )
        return sorted_items[:n]

    @staticmethod
    def _filter_by_name_substring(repos: list[RepoItem], pattern: str | None) -> list[RepoItem]:
        """`name` の部分文字列一致で絞り込む。"""
        if pattern is None or pattern == "":
            return repos
        return [
            item
            for item in repos
            if isinstance(item.get("name"), str) and pattern in cast(str, item["name"])
        ]

    def search_repos(
        self,
        search_name: str,
        name_pattern: str | None = None,
    ) -> list[RepoItem]:
        """検索種別と `--name` 条件でスナップショットを絞り込む。"""
        if search_name not in self.SEARCH_KINDS:
            raise ValueError(f"unsupported search_name: {search_name}")

        assoc = self._load_latest_snapshot_assoc()
        if search_name == "latest10":
            candidates = self._take_latest_n_by_created_at(assoc, 10)
        else:
            candidates = self._filter_by_visibility(assoc, search_name)

        return self._filter_by_name_substring(candidates, name_pattern)
