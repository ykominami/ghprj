from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def parse_created_at(value: object) -> datetime | None:
    """createdAt 値を datetime に変換する。"""
    if not isinstance(value, str) or value == "":
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_snapshot(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"snapshot must be a YAML mapping: {path}")
    return data


def sorted_snapshot_keys(snapshot: dict[str, Any]) -> list[str]:
    def sort_key(item: tuple[str, Any]) -> tuple[bool, float, str]:
        key, value = item
        created_at = None
        if isinstance(value, dict):
            created_at = parse_created_at(value.get("createdAt"))
        return (
            created_at is None,
            -created_at.timestamp() if created_at is not None else 0.0,
            key,
        )

    return [key for key, _ in sorted(snapshot.items(), key=sort_key)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print snapshot.yaml keys sorted by createdAt descending."
    )
    parser.add_argument(
        "snapshot",
        nargs="?",
        default="snapshot.yaml",
        type=Path,
        help="snapshot YAML path",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    for key in sorted_snapshot_keys(load_snapshot(args.snapshot)):
        print(key)


if __name__ == "__main__":
    main()
