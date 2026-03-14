# `add_force_sub_command_list` 外部仕様書

## 1. 目的

`ghrepo` の `list` サブコマンドに対し、保存済みデータの再利用条件と
強制再取得条件を明確化する。
あわせて、`CommandList` の公開メソッド名変更を反映し、利用者から見える
外部仕様を整理する。

本仕様は、`_private/add_force_sub_command_list-requirement.md` の要件を反映し、
既存の `list` / `fix` 系仕様と矛盾しない範囲で `list` サブコマンドの挙動を
補足・更新する。

## 2. 適用範囲

- 対象クラス
  - `Clix`
  - `Ghrepo`
  - `CommandList`
- 対象ファイル構造
  - ユーザディレクトリ
  - `fetch.yaml`
  - `repolist/<count>/db.yaml`
  - 最新状態を表す `db.yaml`

本仕様における保存先の基準パスは、既存仕様に従い
`%LOCALAPPDATA%\\ghrepo\\<user>` とする。

## 3. 用語

### 3.1 ユーザ

`gh auth login` で認証された GitHub アカウントに対応するユーザ名。

### 3.2 ユーザディレクトリ

パス:

```text
%LOCALAPPDATA%\ghrepo\<user>\
```

この配下に、少なくとも以下を持つ。

- `fetch.yaml`
- `repolist/`
- 最新状態を表す `db.yaml`

### 3.3 fetch ファイル

`gh repo list` の成功回数と実行時刻を保持する YAML ファイル。
ファイル名は `fetch.yaml` とする。

### 3.4 リポジトリ一覧スナップショット

ある取得回に対応する保存結果。
保存先は `repolist/<count>/db.yaml` とする。

### 3.5 強制再取得

`list` サブコマンドに `--force` または `-f` が指定されたため、
既存の `fetch.yaml` の有無にかかわらず `gh repo list` を新たに実行すること。

## 4. `list` サブコマンドの実行規則

### 4.1 コマンド形式

```text
ghrepo list [-f|--force] [-v|--verbose] [--user USER] [--limit LIMIT] [--json FIELDS] [--output FILE]
```

### 4.2 `--force` / `-f`

- `--force` は `-f` の長い形式である。
- `--force` または `-f` が指定された場合、実装は `gh repo list` を実行しなければならない。
- `--force` または `-f` が指定されない場合、実装は `fetch.yaml` の存在有無により
  実行可否を判定しなければならない。

### 4.3 `gh repo list` 実行条件

`list` サブコマンド実行時、実装は次の規則に従う。

1. `--force` または `-f` が指定されている場合は、`gh repo list` を実行する。
2. `fetch.yaml` が存在しない場合は、`gh repo list` を実行する。
3. 上記のいずれにも該当しない場合は、`gh repo list` を実行してはならない。

### 4.4 保存済みデータ再利用時の規則

`fetch.yaml` が存在し、かつ `--force` / `-f` が指定されていない場合、
実装は保存済みの最新リポジトリ一覧を利用しなければならない。

このとき:

- 新しいフェッチ回数を採番してはならない。
- `repolist/<count>/db.yaml` を新規作成してはならない。
- `fetch.yaml` を更新してはならない。
- `gh repo list` を実行してはならない。

### 4.5 強制再取得時の保存規則

`gh repo list` を実行した場合、既存仕様に従って以下を満たさなければならない。

1. 新しいフェッチ回数を採番する。
2. `repolist/<count>/db.yaml` を保存する。
3. `fetch.yaml` に `<count>: <timestamp>` を反映する。
4. 最新状態を表す `db.yaml` を取得結果で更新する。

## 5. 公開クラス仕様

## 5.1 `Clix`

責務:

- `ghrepo` CLI のサブコマンドとオプションを定義する。
- `list` サブコマンドの強制再取得オプションを利用可能にする。

### コンストラクタ

```python
Clix(description: str, command_dict: dict[str, Any]) -> None
```

### `list` サブコマンド仕様

コマンド形式:

```text
ghrepo list [-f|--force] [-v|--verbose] [--user USER] [--limit LIMIT] [--json FIELDS] [--output FILE]
```

引数:

- `-f`, `--force`
  - 保存済み `fetch.yaml` が存在していても `gh repo list` を強制実行する。
- `-v`, `--verbose`
  - 実行結果または再利用したデータの要約を標準出力に表示してよい。
- `--user`
  - 対象 GitHub ユーザ名。
- `--limit`
  - `gh repo list` に渡す取得上限。
- `--json`
  - `gh repo list --json` に渡すフィールド列。
- `--output`
  - 出力ファイル名。
  - 本仕様では詳細な保存形式は規定しない。

事後条件:

- `list` サブコマンドは、`-f` と `--force` の両方を受理しなければならない。

## 5.2 `Ghrepo`

責務:

- `list` サブコマンドの実行条件を判定する。
- 必要時のみ `gh repo list` 実行と保存処理を仲介する。
- 再取得不要時は保存済みデータの再利用を仲介する。

### `list_repos`

```python
@classmethod
def list_repos(cls, args: argparse.Namespace) -> None
```

引数:

- `args.force`
- `args.user`
- `args.limit`
- `args.json`
- `args.output`
- `args.verbose`

処理概要:

1. 対象ユーザの `AppStore` を初期化する。
2. `CommandList` を生成する。
3. `args.force` が真であるか、または `fetch.yaml` が存在しない場合に限り、
   `gh repo list` を実行する。
4. `gh repo list` を実行した場合は、新しいスナップショットと `fetch.yaml` を更新する。
5. `gh repo list` を実行しない場合は、保存済みの最新データを利用する。

副作用:

- `gh repo list` 実行時のみ、`fetch.yaml`、`repolist/<count>/db.yaml`、
  最新状態の `db.yaml` が更新される。

事後条件:

- `fetch.yaml` が存在し、`args.force` が偽である場合、
  新たな GitHub CLI 呼び出しは発生してはならない。

## 5.3 `CommandList`

責務:

- `gh repo list` 実行コマンドの構築
- 保存済みフェッチ状態の参照
- 取得結果のスナップショット化
- 最新状態のリポジトリ一覧データの保存

### コンストラクタ

```python
CommandList(appstore: AppStore, json_fields: list[str], user: str | None) -> None
```

### `get_command_for_repository`

```python
def get_command_for_repository(self, args: argparse.Namespace) -> str
```

仕様:

- `gh repo list` に渡す完全なコマンド文字列を返す。
- 戻り値には、少なくとも `--json` を含む。
- 取得上限を適用する場合は `--limit` を含む。
- 対象ユーザが現在設定ユーザと異なる場合は `--user` を含む。

名称変更規則:

- 旧公開名 `get_command_for_project` は、本仕様では廃止とする。
- 実装内で旧名称を呼び出していた箇所は、すべて
  `get_command_for_repository` を参照しなければならない。

### `get_all_repos`

```python
def get_all_repos(
    self,
    args: argparse.Namespace,
    appstore: AppStore,
    count: int,
) -> dict[str, dict[str, Any]]
```

仕様:

- `gh repo list` を実行し、取得した JSON 配列を辞書化して返す。
- コマンド文字列の構築には `get_command_for_repository(args)` を使用しなければならない。
- 返却される各要素には `count`, `valid`, `field_1`, `field_2`, `field_3` を付与する。
- 返却結果は、当該回数の `db.yaml` に保存可能な形式でなければならない。

### `get_fetch_path`

```python
def get_fetch_path(self) -> Path
```

仕様:

- 対象ユーザに対応する `fetch.yaml` のパスを返す。
- `Ghrepo.list_repos(args)` による `fetch.yaml` 存在確認に利用してよい。

### `get_next_snapshot_count`

```python
def get_next_snapshot_count(self) -> int
```

仕様:

- 新しい取得を行う場合にのみ使用される次回フェッチ回数を返す。
- 保存済みデータ再利用時には、この値を確定してはならない。

### `save_snapshot`

```python
def save_snapshot(
    self,
    count: int,
    timestamp: str,
    assoc: dict[str, dict[str, Any]],
) -> None
```

仕様:

- `repolist/<count>/db.yaml` を出力する。
- `fetch.yaml` に `<count>: <timestamp>` を反映する。
- 呼び出し成功後、`fetch.yaml` と `repolist/<count>/db.yaml` は
  整合した状態で存在しなければならない。

## 6. 独立関数仕様

本仕様では、`--force` 追加およびメソッド名変更のために
新規公開が必須となる独立関数は規定しない。

既存の補助関数を内部利用することは妨げないが、
本仕様の公開対象には含めない。

## 7. 正常系の動作要約

### 7.1 初回実行

1. 対象ユーザを確定する。
2. `fetch.yaml` が存在しないことを確認する。
3. `gh repo list` を実行する。
4. 新しいフェッチ回数を採番する。
5. `repolist/<count>/db.yaml`、`fetch.yaml`、最新状態の `db.yaml` を更新する。

### 7.2 強制再取得

1. 対象ユーザを確定する。
2. `args.force` が真であることを確認する。
3. `gh repo list` を実行する。
4. 新しいフェッチ回数を採番する。
5. `repolist/<count>/db.yaml`、`fetch.yaml`、最新状態の `db.yaml` を更新する。

### 7.3 保存済みデータ再利用

1. 対象ユーザを確定する。
2. `fetch.yaml` が存在することを確認する。
3. `args.force` が偽であることを確認する。
4. `gh repo list` を実行せず、保存済み最新データを利用する。
5. `fetch.yaml` とスナップショットは更新しない。

## 8. 異常系

- `gh repo list` 実行失敗時は、新しいフェッチ回数を確定してはならない。
- `gh repo list` 実行失敗時は、対応する `repolist/<count>/db.yaml` と
  `fetch.yaml` を更新してはならない。
- `fetch.yaml` が存在しても、再利用対象の保存済みデータを読めない場合は失敗としてよい。
- 旧名称 `get_command_for_project` を前提にした呼び出しは、
  実装更新後は許容しない。

## 9. 非対象

- `fix` サブコマンドの仕様変更
- `db.yaml` の詳細スキーマ変更
- `--output` の具体的な出力形式定義
- 旧名称との後方互換 API の提供
