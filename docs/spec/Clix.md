# Clix 外部仕様書

## 概要

`ghrepo` の全サブコマンドを登録する CLI ラッパークラス。  
`yklibpy.cli.Cli` をラップし、`setup` / `list` / `fix` / `search` の 4 サブコマンドを定義する。

**モジュール:** `ghrepo.clix`  
**基底クラス:** なし（コンポジション）

---

## 型エイリアス

```python
type CommandHandler = Callable[[argparse.Namespace], None]
```

サブコマンド実行関数の型。`argparse.Namespace` を受け取り `None` を返す。

---

## コンストラクタ

```python
def __init__(self, description: str, command_dict: dict[str, CommandHandler]) -> None
```

### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `description` | `str` | プログラム全体のヘルプ説明文 |
| `command_dict` | `dict[str, CommandHandler]` | サブコマンド名 → 実行関数のマッピング |

### 動作

内部に `Cli` インスタンスを生成し、以下 4 つのサブコマンドを登録する。

---

## 引数の解釈（共通）

- いかなる指定方法であっても、同一の位置引数（必須第 1 引数など）または同一のオプション引数を複数回指定した場合はエラーとする。このエラー判定は、引数仕様のうちで最も優先度が高い。
- 正常系において、オプション引数同士の並び順による意味の違いはない。

---

## サブコマンド

### `setup`

設定ファイルの初期化を行う。

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `--user` | `str` | `None` | GitHub ユーザー名 |

### `list`

全リポジトリ一覧を取得する。

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `-f` / `--force` | フラグ | `False` | 強制ダウンロード |
| `-v` / `--verbose` | フラグ | `False` | 詳細出力 |
| `--user` | `str` | `None` | GitHub ユーザー名 |
| `--limit` | `int` | `None` | 取得件数上限 |
| `--json` | `str` | `None` | 取得フィールドのカンマ区切り指定 |
| `--output` | `str` | `repos.json` | 出力ファイル名 |

### `fix`

保存済みスナップショット構成を補正する。

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `--user` | `str` | `None` | GitHub ユーザー名 |
| `--verbose` | フラグ | `False` | 詳細出力 |

### `search`

必須第 1 引数 `search_name` の値と、指定されたすべての検索条件オプション（`--name` / `--user`）に対応する条件を満たすすべてのリポジトリについて、既定ではリポジトリ名のみを要素とする JSON 配列を標準出力する。`--all` を付けた場合は、リポジトリ情報の全項目を含む JSON 配列を標準出力する。検索対象データは最新の保存スナップショット。

`search_name` が `latest10` の場合は、検索条件オプション `--name` および `--user` の指定は無視する。

| 引数 | 型 | 必須 | 選択肢 | 説明 |
|---|---|---|---|---|
| `search_name` | 位置引数 | Yes | `public` / `private` / `both` / `internal` / `latest10` | 検索種別（下表） |

| `search_name` | 意味 |
|---|---|
| `public` | 可視性（`visibility`）が `public` のリポジトリのみを検索対象にする |
| `private` | 可視性が `private` のリポジトリのみを検索対象にする |
| `both` | 可視性が `public` のものと `private` のものをあわせた集合を検索対象にする（`internal` は含まない） |
| `internal` | 可視性が `internal` のリポジトリのみを検索対象にする |
| `latest10` | 可視性に関係なく、存在するリポジトリのうち直近に登録された最大 10 個までを検索対象にする（10 未満しか存在しなければすべて） |

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `--name` | `str` | `None` | リポジトリ名の部分文字列パターン。リポジトリ名がこのパターンに合致するものに絞り込む（`latest10` では無視） |
| `--user` | `str` | `None` | GitHub ユーザー名。所有者が合致するリポジトリに絞り込む（`latest10` では無視） |
| `--verbose` | フラグ | `False` | 詳細な内容を出力する（デバッグ目的を想定） |
| `--all` | フラグ | `False` | リポジトリ情報のすべての項目を返す（省略時はリポジトリ名のみ） |

---

## メソッド

### `get_subparsers`

```python
def get_subparsers(self, name: str) -> argparse._SubParsersAction[argparse.ArgumentParser]
```

内部 `Cli` が保持する subparsers アクションを返す。

### `parse_args`

```python
def parse_args(self) -> argparse.Namespace
```

登録済み定義に従って CLI 引数を解析し、`argparse.Namespace` を返す。

---

## 利用箇所

`ghrepo.py` の `main()` 関数内で `Clix` をインスタンス化し、`parse_args()` で引数を解析する。
