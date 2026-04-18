# `setup` サブコマンド 外部仕様書

## 1. 目的

`ghrepo` の `setup` サブコマンドに関して、利用者から見える公開仕様を定義する。
本仕様は、コンフィグファイルとユーザディレクトリの初期状態を整え、以後の `list` / `fix` が整合したデータ構造を前提として動作できることを目的とする。

## 2. 適用範囲

- 対象クラス
  - `Clix`
  - `Ghrepo`
  - `CommandSetup`
- 対象ファイル構造
  - コンフィグディレクトリ / コンフィグファイル
  - ユーザディレクトリ配下の初期ファイル

本仕様のファイル名・ディレクトリ名は CLAUDE.md の「用語の定義」および「ディレクトリ/ファイル定義」に準拠する。

## 3. 用語

### 3.1 ユーザ

`gh auth login` で認証された GitHub アカウントに対応するユーザ名。

### 3.2 コンフィグディレクトリ / コンフィグファイル

| 環境 | コンフィグディレクトリ |
|---|---|
| Windows | `%APPDATA%\ghrepo\` |
| Unix 系 | `~/.config/ghrepo/` |

コンフィグファイル: `config.yaml`

コンフィグファイルは必ず以下のキーを持つ。

| キー | 意味 |
|---|---|
| `JSON_FIELDS` | `gh repo list --json` に渡すフィールド一覧 |
| `USER` | 対象 GitHub ユーザ名 |

### 3.3 ユーザディレクトリ

| 環境 | パス |
|---|---|
| Windows | `%LOCALAPPDATA%\ghrepo\<user>\` |
| Unix 系 | `~/.local/share/ghrepo/<user>/` |

### 3.4 初期化対象ファイル

| 用語 | ファイル名 | 格納先 |
|---|---|---|
| コンフィグファイル | `config.yaml` | コンフィグディレクトリ |
| リポジトリ一覧ファイル | `repos.yaml` | ユーザディレクトリ |
| スナップショット作成記録ファイル | `snapshots.yaml` | ユーザディレクトリ |

## 4. 保存構造

### 4.1 ディレクトリ構成（`setup` 完了後）

```text
<コンフィグディレクトリ>
  config.yaml          # JSON_FIELDS と USER を含む

<ユーザディレクトリ>
  repos.yaml           # 空の辞書 {}
  snapshots.yaml       # 空の辞書 {}
  snapshots/           # 以後の `list` 実行で作成される
```

### 4.2 `config.yaml` の初期形式

```yaml
JSON_FIELDS:
  - createdAt
  - description
  - diskUsage
  - hasProjectsEnabled
  - homepageUrl
  - name
  - nameWithOwner
  - owner
  - parent
  - pullRequests
  - url
  - visibility
USER: <ユーザ名>
```

制約:

- `JSON_FIELDS` には少なくとも `visibility` が含まれること。
- `USER` には確定したユーザ名を設定すること。

### 4.3 `repos.yaml` の初期形式

```yaml
{}
```

### 4.4 `snapshots.yaml` の初期形式

```yaml
{}
```

## 5. 整合性ルール

### 5.1 `setup` 成功時

`ghrepo setup` が成功した場合、実装は以下を満たさなければならない。

1. コンフィグディレクトリに `config.yaml` を出力する。
2. `config.yaml` は YAML 連想配列として少なくとも `JSON_FIELDS` と `USER` のキーを持つ。
3. `JSON_FIELDS` には少なくとも `visibility` が含まれること。
4. ユーザディレクトリに `repos.yaml` を空の辞書 `{}` として出力する。
5. ユーザディレクトリに `snapshots.yaml` を空の辞書 `{}` として出力する。

### 5.2 冪等性

`setup` は既に初期化済みの環境に対して再実行されても安全でなければならない。

- `config.yaml` が既に存在する場合は上書きする。
- `repos.yaml` が既に存在する場合は上書きしない（既存データを保護する）。
- `snapshots.yaml` が既に存在する場合は上書きしない（既存データを保護する）。

### 5.3 以後の `list` への前提

本仕様により、次の条件が満たされることが期待される。

- `list` サブコマンドで `--json` を明示指定しない場合でも、`config.yaml` の `JSON_FIELDS` により `visibility` が `--json` に含まれる状態になる。

## 6. 公開クラス仕様

### 6.1 `Clix`

責務: `ghrepo` CLI のサブコマンドとオプションを定義する。

#### コンストラクタ

```python
Clix(description: str, command_dict: dict[str, Any]) -> None
```

事前条件:

- `command_dict` は少なくとも `setup` のキーを持つ。

事後条件:

- `setup` サブコマンドが利用可能になる。

#### `setup` サブコマンド仕様

コマンド形式:

```text
ghrepo setup [--user USER]
```

引数:

| フラグ | 意味 |
|---|---|
| `--user` | 対象ユーザ名。未指定時は認証済み GitHub ユーザを正規化した値を使用する。 |

動作:

- コンフィグディレクトリに `config.yaml` を生成する。
- ユーザディレクトリに `repos.yaml` と `snapshots.yaml` を空の辞書で生成する。

### 6.2 `Ghrepo`

責務: CLI サブコマンドごとに `AppStore` 初期化とコマンド実行を仲介する。

#### `setup`

```python
@classmethod
def setup(cls, args: argparse.Namespace) -> None
```

引数: `args.user`

処理概要:

1. ユーザ名を確定する（`args.user` が未指定の場合は認証済みユーザを使用）。
2. 対象ユーザの `AppStore` を初期化する。
3. `CommandSetup` を生成する。
4. `CommandSetup.run(...)` を呼び出し、`config.yaml`・`repos.yaml`・`snapshots.yaml` を初期化する。

副作用:

- コンフィグディレクトリ・ユーザディレクトリが存在しない場合は作成する。

例外・失敗時:

- ディレクトリが作成できない、または読み書きできない場合は失敗とする。
- YAML 書き込みに失敗した場合は異常終了してよい。

### 6.3 `CommandSetup`

責務: コンフィグファイルと空の保存領域を初期化する。

#### コンストラクタ

```python
CommandSetup(appstore: AppStore) -> None
```

- `appstore`: 対象ユーザディレクトリに結びついた永続化コンテキスト。

#### `run`

```python
def run(self, key: str, default_json_fields: list[str]) -> None
```

引数:

| 引数 | 意味 |
|---|---|
| `key` | `config.yaml` に書き込む設定キー（`"JSON_FIELDS"` 等） |
| `default_json_fields` | `JSON_FIELDS` のデフォルト値として書き込むフィールド一覧 |

仕様:

- コンフィグディレクトリに `config.yaml` を出力する。
- ユーザディレクトリに `repos.yaml` を空の辞書 `{}` で出力する。
- ユーザディレクトリに `snapshots.yaml` を空の辞書 `{}` で出力する。

制約:

- `default_json_fields` には少なくとも `visibility` が含まれること。
- `repos.yaml` および `snapshots.yaml` が既に存在する場合は上書きしない。

## 7. 正常系の動作要約

1. ユーザ名を確定する。
2. コンフィグディレクトリに `config.yaml` を出力する（`JSON_FIELDS` に `visibility` を含める）。
3. ユーザディレクトリに `repos.yaml` を空の辞書 `{}` として出力する（既存時はスキップ）。
4. ユーザディレクトリに `snapshots.yaml` を空の辞書 `{}` として出力する（既存時はスキップ）。

## 8. 異常系

- コンフィグディレクトリまたはユーザディレクトリが作成できない場合は失敗とする。
- YAML の書き込みに失敗した場合は異常終了してよい。
- ユーザ名が確定できない（`gh auth login` 未実施等）場合は、エラーを通知して終了する。

## 9. 非対象

- `list` が保存する `snapshot.yaml` 各レコードの詳細スキーマ拡張
- `fix` の整合性補正アルゴリズム
- `config.yaml` の `JSON_FIELDS` 以外のキーの拡張
