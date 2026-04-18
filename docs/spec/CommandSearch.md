# CommandSearch 外部仕様書

## 概要

保存済みスナップショットから条件に一致するリポジトリを検索するコマンドクラス。  
最新スナップショットを読み込み、可視性・件数・名前の各条件で絞り込みを行う。

コマンドラインの `search` サブコマンドでは、既定では条件に合致したリポジトリの名前のみを JSON 配列で標準出力し、オプション `--all` 指定時は本クラスが返す `RepoItem` 相当の全項目を含む JSON 配列を標準出力する。CLI 側の入出力・重複引数エラー・`latest10` 時の検索条件無視などは `Ghrepo.search_repos` および `Clix` の `search` を参照する。

**モジュール:** `ghrepo.command_search`  
**基底クラス:** `yklibpy.command.Command`

---

## クラス変数

`CommandSearch` のクラス変数として次を持つ。

```python
SEARCH_KINDS: ClassVar[frozenset[str]] = frozenset(
    {"public", "private", "both", "internal", "latest10"}
)
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
def search_repos(
    self,
    search_name: str,
    name_pattern: str | None = None,
    user: str | None = None,
) -> list[RepoItem]
```

最新スナップショットを読み込み、検索種別および検索条件オプションに相当する引数で絞り込み、一致したリポジトリ一覧を返す。

#### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `search_name` | `str` | 検索種別（`SEARCH_KINDS` の値） |
| `name_pattern` | `str \| None` | リポジトリ名の部分文字列パターン（省略可。`latest10` のときは無視） |
| `user` | `str \| None` | GitHub ユーザー名。指定時は所有者がこの値と一致するリポジトリに限定する（省略可。`latest10` のときは無視） |

#### 検索種別の動作

| `search_name` | 動作 |
|---|---|
| `public` | 可視性（`visibility`）が `public` のリポジトリのみを検索対象とする |
| `private` | 可視性が `private` のリポジトリのみを検索対象とする |
| `both` | 可視性が `public` のものと `private` のものをあわせた集合（両方）を検索対象とする |
| `internal` | 可視性が `internal` のリポジトリのみを検索対象とする |
| `latest10` | 可視性に関係なく、存在するリポジトリのうち直近に登録された最大 10 個までを検索対象とする（10 未満しか存在しなければすべて）。並び順・件数は `createdAt` 降順による |

#### `search_name` が `latest10` でない場合の検索条件

`search_name` に応じた可視性による候補に対し、次をすべて満たすリポジトリのみを返す。

- `name_pattern` が指定されている場合: `name` が当該部分文字列を含む（部分文字列一致）
- `user` が指定されている場合: 所有者が当該 GitHub ユーザー名と一致する（`owner` 等の項目から判定）

#### `search_name` が `latest10` の場合

検索条件オプションに相当する `name_pattern` および `user` の指定は無視し、上記 `latest10` の定義どおりに最大 10 件を返す。

#### 戻り値

条件に合致するすべてのリポジトリについて、`RepoItem`（辞書）を要素とするリスト。各辞書はリポジトリ情報の全項目を含む。CLI の `search` で標準出力に出す JSON が「名前のみの配列」か「本戻り値と同様の配列」かは `Ghrepo.search_repos` の `--all` 有無による。

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
`both` を指定すると `public` と `private` の両方が対象になる（`internal` は含まない）。

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
