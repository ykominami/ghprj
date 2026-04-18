# CommandSearch 外部仕様書

## 概要

保存済みスナップショットから条件に一致するリポジトリを検索するコマンドクラス。  
最新スナップショットを読み込み、可視性・件数・名前の各条件で絞り込みを行う。

**モジュール:** `ghrepo.command_search`  
**基底クラス:** `yklibpy.command.Command`

---

## モジュール定数

```python
SEARCH_KINDS = {"public", "private", "both", "internal", "latest10"}
```

`search_repos` の `search_name` 引数として受け付ける検索種別の集合。

---

## 型エイリアス

```python
type RepoItem = dict[str, Any]
type RepoAssoc = dict[str, RepoItem]
```

---

## コンストラクタ

```python
def __init__(self, appstore: AppStore, user: str | None) -> None
```

### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `appstore` | `AppStore` | 設定・DB ファイルアクセスオブジェクト |
| `user` | `str \| None` | 対象 GitHub ユーザー名 |

---

## パブリックメソッド

### `get_snapshots_path`

```python
def get_snapshots_path(self) -> Path
```

`snapshots.yaml` の実ファイルパスを返す。

### `get_user_dir`

```python
def get_user_dir(self) -> Path
```

対象ユーザーの保存ルートディレクトリを返す。

### `get_snapshots_dir`

```python
def get_snapshots_dir(self) -> Path
```

スナップショット保存先の `snapshots` ディレクトリパスを返す。

### `search_repos`

```python
def search_repos(self, search_name: str, name_pattern: str | None = None) -> list[RepoItem]
```

検索種別と名前パターンでスナップショットを絞り込み、一致したリポジトリ一覧を返す。

#### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `search_name` | `str` | 検索種別（`SEARCH_KINDS` の値） |
| `name_pattern` | `str \| None` | リポジトリ名の部分文字列パターン（省略可） |

#### 検索種別の動作

| `search_name` | 動作 |
|---|---|
| `public` | 可視性が `public` のリポジトリを返す |
| `private` | 可視性が `private` のリポジトリを返す |
| `internal` | 可視性が `internal` のリポジトリを返す |
| `both` | 可視性が `public` または `private` のリポジトリを返す |
| `latest10` | `createdAt` 降順で上位 10 件を返す |

#### 戻り値

`RepoItem` (辞書) のリスト。`name_pattern` が指定されている場合は `name` フィールドの部分文字列一致でさらに絞り込まれる。

#### 例外

- `ValueError` — `search_name` が `SEARCH_KINDS` に含まれない場合
- `FileNotFoundError` — スナップショットディレクトリまたはファイルが存在しない場合

---

## スタティックメソッド

### `_collect_snapshot_ids`

```python
@staticmethod
def _collect_snapshot_ids(snapshots_dir: str | Path) -> list[int]
```

`snapshots` ディレクトリ配下の数値ディレクトリ名を昇順で収集して返す。  
数値に解釈できないディレクトリ名は対象外。

### `_filter_by_visibility`

```python
@staticmethod
def _filter_by_visibility(assoc: RepoAssoc, visibility: str) -> list[RepoItem]
```

`visibility` フィールドが一致するレコードを返す。  
`both` を指定すると `public` と `private` の両方が対象になる。

### `_filter_by_name_substring`

```python
@staticmethod
def _filter_by_name_substring(repos: list[RepoItem], pattern: str | None) -> list[RepoItem]
```

`name` フィールドの部分文字列一致で絞り込む。  
`pattern` が `None` または空文字の場合は絞り込みを行わない。

---

## プライベートメソッド

| メソッド | 説明 |
|---|---|
| `_get_store` | ユーザー設定を考慮した `Storex` を返す |
| `_load_latest_snapshot_assoc` | 最新の `snapshot.yaml` を読み込んで `RepoAssoc` を返す |
| `_parse_created_at` | `createdAt` 文字列を `datetime` に変換する（静的） |
| `_take_latest_n_by_created_at` | `createdAt` 降順で上位 n 件を返す |
