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


def remove_empty_directories(root_dir: str | Path) -> int:
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
    def __init__(self, appstore: AppStore, json_fields: list[str], user: str | None) -> None:
        self.appstore = appstore
        self.json_fields = json_fields
        self.user = user
        self.config_user = cast(str, self.appstore.get_from_config("config", "USER"))

    def _get_store(self, base_name: str) -> Storex:
        path_assoc = self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.PATH]
        if self.appstore.user is None:
            return cast(Storex, path_assoc)
        return cast(Storex, path_assoc[self.appstore.user])

    def _set_db_value(self, base_name: str, data: dict[Any, Any]) -> None:
        if self.appstore.user is None:
            self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.VALUE] = data
            return

        self.appstore.file_assoc[AppConfig.KIND_DB][base_name][AppConfig.VALUE][
            self.appstore.user
        ] = data

    def get_fetch_store(self) -> Storex:
        return self._get_store(AppConfig.BASE_NAME_FETCH)

    def get_db_store(self) -> Storex:
        return self._get_store("db")

    def get_fetch_path(self) -> Path:
        return self.get_fetch_store().get_path()

    def get_user_dir(self) -> Path:
        return self.get_fetch_path().parent

    def get_repolist_dir(self) -> Path:
        return self.get_user_dir() / "repolist"

    @staticmethod
    def coerce_fetch_assoc(fetch_assoc: dict[Any, Any]) -> dict[int, str]:
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
        loaded_value = self.get_fetch_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return self.coerce_fetch_assoc(loaded_value)

    def load_latest_assoc(self) -> dict[str, dict[str, Any]]:
        loaded_value = self.get_db_store().load()
        if not isinstance(loaded_value, dict):
            return {}
        return cast(dict[str, dict[str, Any]], loaded_value)

    def output_fetch_assoc(self, fetch_assoc: dict[int, str]) -> None:
        self.appstore.output_db(AppConfig.BASE_NAME_FETCH, fetch_assoc)
        self._set_db_value(AppConfig.BASE_NAME_FETCH, fetch_assoc)

    def get_next_snapshot_count(self) -> int:
        fetch_assoc = self.load_fetch_assoc()
        repolist_counts = collect_repolist_counts(self.get_repolist_dir())
        max_fetch_count = max(fetch_assoc.keys(), default=0)
        max_repolist_count = max(repolist_counts, default=0)
        return max(max_fetch_count, max_repolist_count) + 1

    def get_command_for_repository(self, args: argparse.Namespace) -> str:
        target_user = self.config_user
        if args.user is not None and args.user != "":
            target_user = args.user

        limit_value = 400 if args.limit is None else args.limit
        options = [f"--limit {limit_value}"]

        if args.json is None:
            json_value = ",".join(self.json_fields)
        else:
            json_value = args.json
        options.append(f"--json {json_value}")

        if target_user != "" and target_user != self.config_user:
            options.append(f"--user {target_user}")

        return f"gh repo list {' '.join(options)}"

    @staticmethod
    def array_to_dict(array: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
        return {cast(str, item[key]): item for item in array}

    def get_all_repos(
        self, args: argparse.Namespace, appstore: AppStore, count: int
    ) -> dict[str, dict[str, Any]]:
        del appstore

        command_line = self.get_command_for_repository(args)
        json_str = self.run_command_simple(command_line)
        json_array = json.loads(json_str)
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
        self, count: int, timestamp: str, assoc: dict[str, dict[str, Any]]
    ) -> None:
        snapshot_dir = self.get_repolist_dir() / str(count)
        snapshot_path = snapshot_dir / "db.yaml"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        with snapshot_path.open("w", encoding="utf-8") as snapshot_file:
            yaml.safe_dump(assoc, snapshot_file, allow_unicode=True, sort_keys=True)

        fetch_assoc = self.load_fetch_assoc()
        fetch_assoc[count] = timestamp
        self.output_fetch_assoc(dict(sorted(fetch_assoc.items())))

    def fix_storage(self, verbose: bool = False) -> dict[str, Any]:
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
                print(warning)

        return result
