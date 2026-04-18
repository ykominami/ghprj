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

- `--force` フラグが立っている、または `snapshots.yaml` が存在しない場合に `gh repo list` を実行してスナップショットを保存する。
- それ以外の場合は `gists.yaml` を読み込んで表示する。

---

### `fix_repos`

```python
@classmethod
def fix_repos(cls, args: argparse.Namespace) -> None
```

保存済みスナップショットと DB の整合性を補正する。  
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

保存済みスナップショットから条件一致するリポジトリを検索し、名前リストを JSON 形式で標準出力する。  
`search` サブコマンドのエントリポイント。

#### 引数

| 引数 | 属性 | 型 | 説明 |
|---|---|---|---|
| `args` | `.verbose` | `bool` | 詳細ログ出力フラグ |
| `args` | `.user` | `str \| None` | 対象 GitHub ユーザー名 |
| `args` | `.search_name` | `str` | 検索種別 |
| `args` | `.name` | `str \| None` | 名前の部分文字列パターン |

#### 出力

一致したリポジトリ名のリストを ASCII JSON 形式で標準出力する。

```json
["repo-a", "repo-b"]
```

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

現在の GitHub ユーザー名を正規化してデバッグログに出力する。

`pyproject.toml` のエントリポイント `get_user` に対応する。
