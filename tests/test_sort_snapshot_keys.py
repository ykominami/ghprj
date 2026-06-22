from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sort_snapshot_keys.py"
SPEC = importlib.util.spec_from_file_location("sort_snapshot_keys", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

sorted_snapshot_keys = MODULE.sorted_snapshot_keys


def test_sorted_snapshot_keys_orders_by_created_at_descending() -> None:
    snapshot = {
        "old": {"createdAt": "2024-01-01T00:00:00Z"},
        "new": {"createdAt": "2025-01-01T00:00:00Z"},
        "middle": {"createdAt": "2024-06-01T00:00:00Z"},
    }

    assert sorted_snapshot_keys(snapshot) == ["new", "middle", "old"]


def test_sorted_snapshot_keys_uses_name_for_ties() -> None:
    snapshot = {
        "b": {"createdAt": "2025-01-01T00:00:00Z"},
        "a": {"createdAt": "2025-01-01T00:00:00Z"},
    }

    assert sorted_snapshot_keys(snapshot) == ["a", "b"]


def test_sorted_snapshot_keys_puts_missing_or_invalid_created_at_last() -> None:
    snapshot = {
        "missing": {},
        "valid": {"createdAt": "2025-01-01T00:00:00Z"},
        "invalid": {"createdAt": "not-a-date"},
    }

    assert sorted_snapshot_keys(snapshot) == ["valid", "invalid", "missing"]
