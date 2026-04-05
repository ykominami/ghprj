from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml
from yklibpy.command import Command
from yklibpy.config.appconfig import AppConfig
from yklibpy.db.appstore import AppStore
from yklibpy.db.storex import Storex

from ghrepo.command_list import collect_repolist_counts

type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]

SEARCH_KINDS = {"public", "private", "internal", "latest10"}


def load_latest_snapshot_assoc(repolist_dir: str | Path) -> RepoAssoc:
    """最新スナップショットの `db.yaml` を読み込んで返す。"""
    repolist_path = Path(repolist_dir)
    repolist_counts = collect_repolist_counts(repolist_path)
    if not repolist_counts:
        raise FileNotFoundError(f"no snapshot directories found: {repolist_path}")

    latest_count = max(repolist_counts)
    snapshot_path = repolist_path / str(latest_count) / "db.yaml"
    if not snapshot_path.exists():
        raise FileNotFoundError(f"latest snapshot does not exist: {snapshot_path}")

    with snapshot_path.open(encoding="utf-8") as snapshot_file:
        loaded_value = yaml.safe_load(snapshot_file)
    if not isinstance(loaded_value, dict):
        raise ValueError(f"snapshot must be an assoc dict: {snapshot_path}")

    assoc: RepoAssoc = {}
    for key, value in loaded_value.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        assoc[key] = cast(RepoItem, value)
    return assoc


def filter_by_visibility(assoc: RepoAssoc, visibility: str) -> list[RepoItem]:
    """`visibility` が一致するレコードを返す。"""
    normalized_visibility = visibility.lower()
    return [
        item
        for item in assoc.values()
        if isinstance(item.get("visibility"), str)
        and cast(str, item["visibility"]).lower() == normalized_visibility
    ]


def _parse_created_at(value: object) -> datetime | None:
    """`createdAt` 値を `datetime` に変換する。"""
    if not isinstance(value, str) or value == "":
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def take_latest_n_by_created_at(assoc: RepoAssoc, n: int) -> list[RepoItem]:
    """`createdAt` 降順で上位 `n` 件を返す。"""
    items = list(assoc.values())
    sorted_items = sorted(
        items,
        key=lambda item: (
            _parse_created_at(item.get("createdAt")) is None,
            -(cast(datetime, _parse_created_at(item.get("createdAt"))).timestamp())
            if _parse_created_at(item.get("createdAt")) is not None
            else 0.0,
            str(item.get("name", "")),
        ),
    )
    return sorted_items[:n]


def filter_by_name_substring(repos: list[RepoItem], pattern: str | None) -> list[RepoItem]:
    """`name` の部分文字列一致で絞り込む。"""
    if pattern is None or pattern == "":
        return repos
    return [
        item
        for item in repos
        if isinstance(item.get("name"), str) and pattern in cast(str, item["name"])
    ]


class CommandSearch(Command):
    """保存済みスナップショットを検索するコマンド。"""

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

    def get_fetch_path(self) -> Path:
        """`fetch` DB の実ファイルパスを返す。"""
        return self._get_store(AppConfig.BASE_NAME_FETCH).get_path()

    def get_user_dir(self) -> Path:
        """対象ユーザーの保存ルートディレクトリを返す。"""
        return self.get_fetch_path().parent

    def get_repolist_dir(self) -> Path:
        """スナップショット保存先の `repolist` ディレクトリを返す。"""
        return self.get_user_dir() / "repolist"

    def search_repos(
        self,
        search_name: str,
        name_pattern: str | None = None,
    ) -> list[RepoItem]:
        """検索種別と `--name` 条件でスナップショットを絞り込む。"""
        if search_name not in SEARCH_KINDS:
            raise ValueError(f"unsupported search_name: {search_name}")

        assoc = load_latest_snapshot_assoc(self.get_repolist_dir())

        if search_name == "latest10":
            candidates = take_latest_n_by_created_at(assoc, 10)
        else:
            candidates = filter_by_visibility(assoc, search_name)

        return filter_by_name_substring(candidates, name_pattern)

