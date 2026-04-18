# Ghrepo 外部仕様書

## 概要

`ghrepo` CLI の主要処理を束ねる統括クラス。  
`AppStore` の初期化、各サブコマンド（`setup` / `list` / `fix` / `search`）の実行を担う。  
すべてのメソッドはクラスメソッドとして実装されており、インスタンス化は不要。

**モジュール:** `ghrepo.ghrepo`  
**基底クラス:** なし

---

## クラスメソッド

### `init_appstore`

```python
@classmethod
def init_appstore(cls, normalized_user: str | None) -> AppStore
```

対象ユーザーに対応する `AppStore` を準備して返す。

#### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `normalized_user` | `str \| None` | 正規化済み GitHub ユーザー名。`None` の場合は `gh auth` から取得する |

#### 動作

1. `Storex` にファイル種別辞書を設定する。
2. `normalized_user` が `None` の場合は `CommandGhUser().run()` でユーザー名を取得する。取得できない場合は `CommandGhUser.DEFAULT_VALUE_USER` を使用する。
3. `AppStore("ghrepo", ...)` を初期化し、設定ファイル・DB ファイルを準備する。

#### 戻り値

設定ファイルと DB ファイルの準備が完了した `AppStore`。

---

### `setup`

```python
@classmethod
def setup(cls, args: argparse.Namespace) -> None
```

設定ファイルと保存先 DB の初期化を実行する。  
`setup` サブコマンドのエントリポイント。

#### 引数

| 引数 | 属性 | 型 | 説明 |
|---|---|---|---|
| `args` | `.user` | `str \| None` | 対象 GitHub ユーザー名 |

---

### `list_repos`

```python
@classmethod
def list_repos(cls, args: argparse.Namespace) -> None
```

GitHub リポジトリ一覧を取得し、最新 DB とスナップショットを更新する。  
`list` サブコマンドのエントリポイント。

#### 引数

| 引数 | 属性 | 型 | 説明 |
|---|---|---|---|
| `args` | `.verbose` | `bool` | 詳細ログを出力するか |
| `args` | `.user` | `str \| None` | 対象 GitHub ユーザー名 |
| `args` | `.force` | `bool` | 強制ダウンロードフラグ |
| `args` | `.limit` | `int \| None` | 取得件数上限 |
| `args` | `.json` | `str \| None` | カンマ区切りフィールド指定 |

#### 動作

- `--force` フラグが立っている、または `snapshots.yaml` が存在しない場合に `gh repo list` を実行してスナップショットを保存し、`repos.yaml` 等を更新する。
- それ以外の場合は既存の `repos.yaml` を読み込み、`--output` で指定したファイルへ JSON を書き出す。

---

### `fix_repos`

```python
@classmethod
def fix_repos(cls, args: argparse.Namespace) -> None
```

空ディレクトリの削除と `snapshots.yaml` の整合性補正を行う。`repos.yaml` は変更しない。  
`fix` サブコマンドのエントリポイント。

#### 引数

| 引数 | 属性 | 型 | 説明 |
|---|---|---|---|
| `args` | `.verbose` | `bool` | 詳細ログ出力フラグ |
| `args` | `.user` | `str \| None` | 対象 GitHub ユーザー名 |

---

### `search_repos`

```python
@classmethod
def search_repos(cls, args: argparse.Namespace) -> None
```

保存済みスナップショットから、必須第 1 引数 `search_name` の値と、指定されたすべての検索条件オプション（`--name` / `--user`）に対応する条件を満たすリポジトリを検索し、結果を JSON 配列で標準出力する。  
`search` サブコマンドのエントリポイント。

引数の重複指定や優先度、オプションの順序に関する規則は `Clix` の「引数の解釈（共通）」および `search` サブコマンド定義に従う。

#### 引数

| 引数 | 属性 | 型 | 説明 |
|---|---|---|---|
| `args` | `.verbose` | `bool` | 詳細な内容を出力する（デバッグ目的を想定） |
| `args` | `.user` | `str \| None` | 検索条件としての GitHub ユーザー名（所有者が合致するリポジトリに限定。`search_name` が `latest10` のときは無視） |
| `args` | `.search_name` | `str` | 検索種別（`public` / `private` / `both` / `internal` / `latest10`） |
| `args` | `.name` | `str \| None` | リポジトリ名の部分文字列パターン（`latest10` のときは無視） |
| `args` | `.all` | `bool` | `True` のときはリポジトリ情報の全項目を含む JSON 配列を標準出力する |

#### 出力

- **既定（`.all` が偽）:** 条件に合致するすべてのリポジトリについて、**リポジトリ名のみ** を要素とする JSON 配列（ASCII）を標準出力する。

```json
["repo-a", "repo-b"]
```

- **`.all` が真:** 条件に合致する各リポジトリについて、`CommandSearch.search_repos` が返す `RepoItem` と同様の全項目を含むオブジェクトの JSON 配列を標準出力する。

---

## プライベートクラスメソッド

| メソッド | 説明 |
|---|---|
| `_set_log_level_by_verbose` | `verbose` フラグに応じてログレベルを `DEBUG` / `INFO` に切り替える |
| `_debug_if_verbose` | `verbose` が有効な場合のみ整形済み JSON をデバッグ出力する |

---

## モジュールレベル関数

### `main`

```python
def main() -> None
```

CLI エントリポイント。`Clix` で引数を解析し、選択されたサブコマンドを実行する。

`pyproject.toml` のエントリポイント `ghrepo` に対応する。

### `get_user`

```python
def get_user() -> None
```

正規化した GitHub ユーザー名を `Loggerx.debug` に出力する。標準出力には出さず、ログレベルが DEBUG のときのみ表示される。

`pyproject.toml` のエントリポイント `get_user` に対応する。
