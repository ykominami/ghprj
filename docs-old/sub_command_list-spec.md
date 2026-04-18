# `list` サブコマンド 外部仕様書

## 1. 目的

`ghrepo` の `list` / `fix` サブコマンドに関して、利用者から見える公開仕様を定義する。
本仕様は、`gh repo list` の実行結果を世代管理し、保存済みデータの整合性を回復できることを目的とする。

## 2. 適用範囲

- 対象クラス
  - `Clix`
  - `Ghrepo`
  - `CommandList`
- 対象ファイル構造
  - ユーザディレクトリ配下の全ファイル・ディレクトリ

本仕様のファイル名・ディレクトリ名は CLAUDE.md の「用語の定義」および「ディレクトリ/ファイル定義」に準拠する。

## 3. 用語

### 3.1 ユーザ

`gh auth login` で認証された GitHub アカウントに対応するユーザ名。

### 3.2 コンフィグディレクトリ / コンフィグファイル

| 環境 | コンフィグディレクトリ |
|---|---|
| Windows | `%APPDATA%\ghrepo\` |
| Unix 系 | `~/.config/ghrepo/` |

コンフィグファイル: `config.yaml`（キー: `JSON_FIELDS`, `USER`）

### 3.3 ユーザディレクトリ

| 環境 | パス |
|---|---|
| Windows | `%LOCALAPPDATA%\ghrepo\<user>\` |
| Unix 系 | `~/.local/share/ghrepo/<user>/` |

### 3.4 スナップショットID

`gh repo list` の成功回数を表す正の整数。`1, 2, 3, ...` のように単調増加する。

### 3.5 ファイル・ディレクトリ一覧

| 用語 | ファイル名 / ディレクトリ名 |
|---|---|
| リポジトリ一覧ファイル | `gists.yaml` |
| スナップショット作成記録ファイル | `snapshots.yaml` |
| スナップショットトップディレクトリ | `snapshots/` |
| 個別スナップショットディレクトリ | `<スナップショットID>/` |
| リポジトリ一覧スナップショットファイル | `snapshot.yaml` |

## 4. 保存構造

### 4.1 ディレクトリ構成

```text
<ユーザディレクトリ>
  gists.yaml
  snapshots.yaml
  snapshots/
    1/
      snapshot.yaml
    2/
      snapshot.yaml
    ...
```

### 4.2 `snapshots.yaml` の形式

YAML の連想配列。キーをスナップショットID、値を成功時刻のタイムスタンプ文字列とする。

```yaml
1: "2026-03-08T09:15:30+09:00"
2: "2026-03-08T10:02:11+09:00"
```

制約:

- キーは 10 進表記の正の整数でなければならない。
- 値は成功時刻を表す文字列でなければならない。
- 最大キーは、存在する `snapshots/<スナップショットID>` のうち最大の数値ディレクトリ名と一致しなければならない。

### 4.3 `snapshots/<snapshot-id>/snapshot.yaml` の形式

トップレベルはリポジトリID をキーとする連想配列。各値は少なくとも以下のキーを持つ。

- `snapshot-id` — 親ディレクトリのスナップショットIDと一致する正の整数
- `name` — リポジトリ名
- `visibility` — `public` / `private` / `internal` のいずれか（小文字）
- `valid` — 常に `True`
- `field_1`, `field_2`, `field_3` — 空文字列（ユーザ注記用）
- `JSON_FIELDS` で指定された GitHub 応答項目

形式例:

```yaml
<repo-id>:
  snapshot-id: 1
  createdAt: '2018-04-30T07:27:49Z'
  description: リポジトリの説明
  diskUsage: 12
  field_1: ''
  field_2: ''
  field_3: ''
  name: my-repo
  nameWithOwner: ykominami/my-repo
  owner:
    id: MDQ6VXNlcjEwNjE3OQ==
    login: ykominami
  url: https://github.com/ykominami/my-repo
  valid: true
  visibility: public
```

制約:

- `visibility` の値は `gh repo list` から取得した値を小文字化して保存する。
- `internal` は `internal` のままとし、他の値へ変換してはならない。
- 各要素の `snapshot-id` は、親ディレクトリ名の整数値と一致しなければならない。

### 4.4 `gists.yaml` の形式

`snapshot.yaml` と同一のフォーマット。

各リポジトリ一覧スナップショットファイルを、スナップショットIDの昇順（古いものから新しいもの）にマージした結果を保持する。同一リポジトリIDのレコードが存在した場合、内容に差異があれば新しいレコードで更新する。差異がなければ更新しない。

## 5. visibility 取得・保存ルール

`gh repo list` の実行時は、ユーザの `--json` 指定にかかわらず `visibility` を必ず取得・保存すること。

- `public`、`private`、`internal` のいずれかの値を小文字のまま保存する。
- `internal` を `public` や `private` に変換してはならない。
- `gh repo list --json` に渡すフィールド列に `visibility` が含まれていない場合、実装は `visibility` を強制的に追加する。

## 6. 整合性ルール

### 6.1 `list` 成功時

`gh repo list` が成功した場合、実装は以下を満たさなければならない。

1. 新しいスナップショットIDを確定する（既存最大値 + 1）。
2. `snapshots/<snapshot-id>/snapshot.yaml` を出力する。
3. `snapshots.yaml` に `<snapshot-id>: <timestamp>` を追加または更新する。
4. `gists.yaml` を新スナップショット内容でマージ更新する。

更新の順序は、「`snapshots.yaml` に記録されているIDに対して、対応する `snapshot.yaml` が存在する」状態を保証しなければならない。

### 6.2 `fix` 実行時

`fix` は、ユーザディレクトリ配下を検査し、以下の整合性を回復する。

1. 空ディレクトリを再帰的に削除する。
2. `snapshots/` 直下の数値ディレクトリ名の最大値を求める。
3. `snapshots.yaml` にその最大値のエントリが存在しない場合は追加する。
4. `snapshots.yaml` の最大キーが上記最大値より大きい場合は修正する。

補足:

- `fix` は既存の `snapshot.yaml` 内容を書き換えない。
- タイムスタンプを再構成できない場合は、既存最大エントリの値または実行時刻を使用してよい。ただし補完規則は固定でなければならない。
- 数値に解釈できないディレクトリ名は回数算出対象に含めない。

### 6.3 削除規則

- `fix` は空ディレクトリのみ削除してよい。
- `snapshot.yaml` を含むディレクトリ、または非空ディレクトリは削除してはならない。
- `snapshots.yaml` の既存エントリは、最大値整合のために必要な場合を除き削除してはならない。

## 7. 公開クラス仕様

### 7.1 `Clix`

責務: `ghrepo` CLI のサブコマンドとオプションを定義する。

#### コンストラクタ

```python
Clix(description: str, command_dict: dict[str, Any]) -> None
```

事前条件:

- `command_dict` は少なくとも `setup`, `list`, `fix` の各キーを持つ。

事後条件:

- `setup`, `list`, `fix` の各サブコマンドが利用可能になる。

#### `list` サブコマンド仕様

コマンド形式:

```text
ghrepo list [-f] [-v] [--user USER] [--limit N] [--json FIELDS] [--output FILE]
```

引数:

| フラグ | 意味 |
|---|---|
| `-f` / `--force` | キャッシュを無視して強制取得する |
| `-v` / `--verbose` | 詳細情報を表示する |
| `--user` | 対象ユーザ名（未指定時は認証済みユーザ） |
| `--limit` | 取得上限数 |
| `--json` | 追加取得フィールド（`visibility` は常に含まれる） |
| `--output` | 結果の出力先ファイル |

#### `fix` サブコマンド仕様

コマンド形式:

```text
ghrepo fix [--user USER] [--verbose]
```

引数:

| フラグ | 意味 |
|---|---|
| `--user` | 対象ユーザ名（未指定時は認証済みユーザ） |
| `--verbose` | 修復前後の要約情報を標準出力に表示する |

動作:

- ユーザディレクトリ配下の保存構造を検査する。
- 空ディレクトリを再帰的に削除する。
- `snapshots.yaml` と `snapshots/` 直下の最大回数を整合させる。

### 7.2 `Ghrepo`

責務: CLI サブコマンドごとに `AppStore` 初期化とコマンド実行を仲介する。

#### `main`

```python
main() -> None
```

- 引数を解析し、選択されたサブコマンドに対応するメソッドを呼び出す。
- `list` が指定された場合は `Ghrepo.list_repos(args)` を呼び出す。
- `fix` が指定された場合は `Ghrepo.fix_repos(args)` を呼び出す。

#### `list_repos`

```python
@classmethod
def list_repos(cls, args: argparse.Namespace) -> None
```

処理概要:

1. 対象ユーザの `AppStore` を初期化する。
2. `CommandList` を生成する。
3. `CommandList.get_all_repos(...)` を呼び出す。
4. `CommandList.save_snapshot(...)` を呼び出す。

#### `fix_repos`

```python
@classmethod
def fix_repos(cls, args: argparse.Namespace) -> None
```

引数: `args.user`, `args.verbose`

処理概要:

1. 対象ユーザの `AppStore` を初期化する。
2. `CommandList` を生成する。
3. `CommandList.fix_storage(...)` を呼び出す。
4. 必要に応じて修復結果を表示する。

副作用:

- ユーザディレクトリ配下の空ディレクトリを削除する。
- `snapshots.yaml` を更新する。

例外・失敗時:

- ユーザディレクトリが読み書きできない場合は失敗とする。
- YAML 読み込みに失敗した場合は原因を利用者に通知して異常終了する。

### 7.3 `CommandList`

責務:

- `gh repo list` 実行コマンドの構築
- 取得結果のスナップショット化
- `snapshots.yaml`、`snapshots/<snapshot-id>/snapshot.yaml`、`gists.yaml` の整合的な更新
- `fix` サブコマンドによる保存構造の修復

#### コンストラクタ

```python
CommandList(appstore: AppStore, json_fields: list[str], user: str | None) -> None
```

- `appstore`: 対象ユーザディレクトリに結びついた永続化コンテキスト
- `json_fields`: `gh repo list --json` に渡すフィールド一覧
- `user`: CLI で明示指定されたユーザ名。`None` または空文字列の場合は設定値を用いる。

#### `get_command_for_repository`

```python
def get_command_for_repository(self, args: argparse.Namespace) -> str
```

- `gh repo list` に渡す完全なコマンド文字列を返す。
- `--json` で指定されたフィールド列に `visibility` が含まれていない場合、強制的に追加する。
- 対象ユーザが現在ユーザと異なる場合は `--user` を含める。
- 取得上限を適用する場合は `--limit` を含める。

#### `get_all_repos`

```python
def get_all_repos(
    self,
    args: argparse.Namespace,
    appstore: AppStore,
    snapshot_id: int,
) -> dict[str, dict[str, Any]]
```

- `gh repo list` を実行し、取得した JSON 配列を辞書化して返す。
- 取得結果の各要素は `visibility` を含み、値は `public` / `private` / `internal` のいずれかであること。
- `internal` はそのまま `internal` として返すこと。
- 返却される各要素には `snapshot-id`, `valid`, `field_1`, `field_2`, `field_3` を付与する。

#### `save_snapshot`

```python
def save_snapshot(
    self,
    snapshot_id: int,
    timestamp: str,
    assoc: dict[str, dict[str, Any]],
) -> None
```

- `snapshots/<snapshot-id>/snapshot.yaml` を出力する。
- `snapshots.yaml` に `<snapshot-id>: <timestamp>` を反映する。
- `gists.yaml` を新スナップショット内容でマージ更新する。
- 呼び出し成功後、`snapshots.yaml` と `snapshots/<snapshot-id>/snapshot.yaml` は整合した状態で存在しなければならない。

#### `fix_storage`

```python
def fix_storage(self, verbose: bool = False) -> dict[str, Any]
```

戻り値の必須キー:

| キー | 型 | 意味 |
|---|---|---|
| `removed_empty_directories` | `int` | 削除した空ディレクトリ数 |
| `max_snapshot_id` | `int \| None` | `snapshots/` 直下の最大スナップショットID |
| `snapshots_updated` | `bool` | `snapshots.yaml` を更新したか |
| `warnings` | `list[str]` | 処理中の警告一覧 |

処理概要:

1. ユーザディレクトリ配下を再帰走査する。
2. 空ディレクトリを削除する（`remove_empty_directories` の内部実装を用いる）。
3. `snapshots/` 直下の数値ディレクトリ名を収集する（`collect_snapshot_ids` の内部実装を用いる）。
4. 最大値に基づいて `snapshots.yaml` を補正する（`normalize_snapshots_assoc` の内部実装を用いる）。
5. 実施内容を要約して返す。

例外・失敗時:

- `snapshots.yaml` が YAML として不正なら例外を送出してよい。
- `snapshots/` 不在時は警告付きで空集合として扱ってよい。

## 8. 正常系の動作要約

### 8.1 `ghrepo list`

1. ユーザを確定する。
2. `gh repo list` を実行する（`--json` に `visibility` を強制含め）。
3. 新しいスナップショットIDを採番する。
4. `snapshots/<snapshot-id>/snapshot.yaml` を保存する。
5. `snapshots.yaml` を更新する。
6. `gists.yaml` をマージ更新する。

### 8.2 `ghrepo fix`

1. ユーザを確定する。
2. 空ディレクトリを削除する。
3. `snapshots/` の最大スナップショットIDを求める。
4. `snapshots.yaml` を補正する。
5. 必要に応じて要約を表示する。

## 9. 異常系

- GitHub CLI 実行失敗時は、新しいスナップショットIDを確定してはならない。
- `snapshot.yaml` 保存失敗時は、対応する `snapshots.yaml` エントリだけが残る状態にしてはならない。
- `fix` 実行中に一部の空ディレクトリ削除に失敗しても、継続可能な範囲では処理継続を許容する。ただし警告を返すこと。
- `snapshots.yaml` が存在しない場合、`fix` は空の YAML 連想配列として再生成してよい。

## 10. 非対象

- `snapshot.yaml` の各リポジトリ項目の詳細スキーマ拡張
- リポジトリ一覧の差分表示 UI
- 壊れた `snapshot.yaml` 内容の自動修復
