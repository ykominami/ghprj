# CommandList 外部仕様書

## 概要

リポジトリ一覧の取得・保存・補正を担当するコマンドクラス。  
`gh repo list` の実行、スナップショット保存、`repos.yaml`（リポジトリ一覧ファイル）のマージ更新、ストレージ整合性補正を提供する。

**モジュール:** `ghrepo.command_list`  
**基底クラス:** `yklibpy.command.Command`

---

## 型エイリアス

```python
type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]
```

---

## コンストラクタ

```python
def __init__(self, appstore: AppStore, json_fields: list[str], user: str | None) -> None
```

### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `appstore` | `AppStore` | 設定・DB ファイルアクセスオブジェクト |
| `json_fields` | `list[str]` | `gh repo list --json` へ渡すフィールド名リスト |
| `user` | `str \| None` | 対象 GitHub ユーザー名（`None` の場合は設定値を使用） |

---

## パブリックメソッド

### `get_snapshots_store`

```python
def get_snapshots_store(self) -> Storex
```

`snapshots.yaml` に対応する `Storex` を返す。

### `get_repos_store`

```python
def get_repos_store(self) -> Storex
```

`repos.yaml` に対応する `Storex` を返す。

### `get_snapshots_path`

```python
def get_snapshots_path(self) -> Path
```

`snapshots.yaml` の実ファイルパスを返す。

### `get_user_dir`

```python
def get_user_dir(self) -> Path
```

対象ユーザーの保存ルートディレクトリ（ユーザーディレクトリ）を返す。

### `get_snapshots_dir`

```python
def get_snapshots_dir(self) -> Path
```

スナップショット保存先の `snapshots` ディレクトリパスを返す。

### `get_next_snapshot_id`

```python
def get_next_snapshot_id(self) -> int
```

`snapshots.yaml` に記録された ID とスナップショットディレクトリ上の ID の最大値のいずれか大きい方に 1 を加えた、次に採番するスナップショット ID を返す。

### `get_command_for_repository`

```python
def get_command_for_repository(self, args: argparse.Namespace) -> str
```

CLI 引数と設定値から実行すべき `gh repo list` コマンド文字列を組み立てて返す。

- `--limit` 未指定時は 400 を使用する。
- `--json` 未指定時は `self.json_fields` を使用する。
- `visibility` フィールドは常に強制追加する（重複は除去）。

### `load_latest_assoc`

```python
def load_latest_assoc(self) -> RepoAssoc
```

`repos.yaml` を読み込み、リポジトリ名をキーとする辞書として返す。

### `get_all_repos`

```python
def get_all_repos(self, args: argparse.Namespace, appstore: AppStore, snapshot_id: int) -> RepoAssoc
```

`gh repo list` を実行し、各アイテムに管理フィールドを付与して返す。

**付与する管理フィールド:**

| フィールド | 値 |
|---|---|
| `snapshot-id` | 引数 `snapshot_id` |
| `valid` | `True` |
| `field_1` | `""` |
| `field_2` | `""` |
| `field_3` | `""` |

**`visibility` の正規化:** `PUBLIC` 等の大文字を `public` / `private` / `internal` の小文字に統一する。

**例外:**
- `ValueError` — JSON パース失敗、`name` / `visibility` フィールド欠損、`visibility` 値が不正

### `save_snapshot`

```python
def save_snapshot(self, snapshot_id: int, timestamp: str, assoc: RepoAssoc) -> None
```

取得結果をスナップショットとして永続化する。

**保存順序:**

1. `snapshots/<snapshot-id>/snapshot.yaml` を出力する。
2. `snapshots.yaml` に `<snapshot-id>: <timestamp>` を反映する。
3. `repos.yaml` をマージ更新する（同一 repo-id の差分がある場合のみ上書き）。

### `fix_storage`

```python
def fix_storage(self, verbose: bool = False) -> dict[str, Any]
```

保存済みスナップショット構成を点検・補正する。

**戻り値（辞書）:**

| キー | 型 | 説明 |
|---|---|---|
| `removed_empty_directories` | `int` | 削除した空ディレクトリ数 |
| `max_snapshot_id` | `int \| None` | ディレクトリ上の最大スナップショット ID |
| `snapshots_record_updated` | `bool` | `snapshots.yaml` を更新したか |
| `warnings` | `list[str]` | 警告メッセージ一覧 |

---

## スタティックメソッド

### `array_to_dict`

```python
@staticmethod
def array_to_dict(array: list[RepoItem], key: str) -> RepoAssoc
```

リポジトリ配列を指定キー基準の連想配列（辞書）へ変換する。

### `_remove_empty_directories`

```python
@staticmethod
def _remove_empty_directories(root_dir: str | Path) -> int
```

指定ディレクトリ配下の空ディレクトリを末端から削除し、削除件数を返す。

### `_collect_snapshot_ids`

```python
@staticmethod
def _collect_snapshot_ids(snapshots_dir: str | Path) -> list[int]
```

`snapshots` ディレクトリ配下の数値ディレクトリ名を昇順で収集して返す。  
数値に解釈できないディレクトリ名は対象外。

### `_normalize_snapshots_record_assoc`

```python
@staticmethod
def _normalize_snapshots_record_assoc(
    snapshots_assoc: dict[Any, Any],
    snapshot_ids: list[int],
    fallback_timestamp: str,
) -> tuple[dict[int, str], bool]
```

`snapshots.yaml` の内容を型整形し、ディレクトリ上の最大 ID に合わせて余分な ID の除去や欠落エントリの補完を行う。

**戻り値:** `(正規化済み辞書, 変更があったか)`

---

## プライベートメソッド

| メソッド | 説明 |
|---|---|
| `_get_store` | ユーザー設定を考慮した `Storex` を返す |
| `_set_db_value` | `AppStore` 内キャッシュ値を更新する |
| `_load_snapshots_assoc` | `snapshots.yaml` を読み込み正規化して返す |
| `_output_snapshots_assoc` | `snapshots.yaml` を永続化し内部値を同期する |
| `_merge_into_repos` | `repos.yaml` に新スナップショットをマージ更新する |
| `_coerce_snapshots_record_assoc` | 辞書キー・値を保存型へ型整形のみ行う（静的）。`_normalize_snapshots_record_assoc` はこれに加え、余分な ID の除去や最大 ID エントリの補完も行う |
