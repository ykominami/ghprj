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

最新スナップショットからリポジトリを検索する。

| 引数 | 型 | 必須 | 選択肢 | 説明 |
|---|---|---|---|---|
| `search_name` | 位置引数 | Yes | `public` / `private` / `both` / `internal` / `latest10` | 検索種別 |

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `--name` | `str` | `None` | リポジトリ名の部分文字列パターン |
| `--user` | `str` | `None` | GitHub ユーザー名 |
| `--verbose` | フラグ | `False` | 詳細出力 |

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
