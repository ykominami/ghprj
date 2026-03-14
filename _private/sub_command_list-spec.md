# `sub_command_list` 外部仕様書

## 1. 目的

`ghrepo` の `list` / `fix` サブコマンドに関して、利用者から見える公開仕様を定義する。
本仕様は、`gh repo list` の実行結果を世代管理し、保存済みデータの整合性を回復できることを目的とする。

## 2. 適用範囲

- 対象クラス
  - `Clix`
  - `Ghrepo`
  - `CommandList`
- 対象ファイル構造
  - ユーザディレクトリ
  - `fetch.yaml`
  - `repolist/<count>/db.yaml`
- 必要に応じて公開する独立関数

本仕様では、`_private/sub_command_list-requirement.md` を主とし、`_private/command_list_requirement.md` の `fix` 要件を補完的に採用する。
保存先の基準パスは `%LOCALAPPDATA%\\ghrepo\\<user>` とする。
`AppData\\Local\\gistx\\repo` という記述は旧名称または誤記として扱い、本仕様では採用しない。

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

### 3.3 フェッチ回数

`gh repo list` の成功回数を表す正の整数。
`1, 2, 3, ...` のように単調増加する。

### 3.4 リポジトリ一覧スナップショット

あるフェッチ回数に対応する `gh repo list` の保存結果。
保存先は `repolist/<count>/db.yaml` とする。

## 4. 保存構造

### 4.1 ディレクトリ構成

```text
%LOCALAPPDATA%\ghrepo\<user>\
  fetch.yaml
  repolist\
    1\
      db.yaml
    2\
      db.yaml
    ...
```

### 4.2 `fetch.yaml` の形式

YAML の連想配列とし、キーをフェッチ回数、値を成功時刻のタイムスタンプ文字列とする。

例:

```yaml
1: "2026-03-08T09:15:30+09:00"
2: "2026-03-08T10:02:11+09:00"
```

制約:

- キーは 10 進表記の正の整数でなければならない。
- 値は、成功時刻を表す文字列でなければならない。
- 最大キーは、存在する `repolist/<count>` のうち最大の数値ディレクトリ名と一致しなければならない。

### 4.3 `repolist/<count>/db.yaml` の形式

- `<count>` は正の整数のディレクトリ名である。
- `db.yaml` は、その回の `gh repo list` 実行結果を保存する YAML ファイルである。
- `db.yaml` のトップレベル形式は、既存の `db` ストア互換の連想配列とする。
- キーはリポジトリ名、値は各リポジトリのメタデータ辞書とする。

各値は少なくとも以下のキーを持つ。

- `name`
- `count`
- `valid`
- `field_1`
- `field_2`
- `field_3`
- 既存 `JSON_FIELDS` で要求される GitHub 応答項目

制約:

- 各要素の `count` は、親ディレクトリ名 `<count>` と一致しなければならない。
- `db.yaml` は、対応する `fetch.yaml` エントリが存在する回数に対して保存される。

## 5. 整合性ルール

### 5.1 `list` 成功時

`gh repo list` が成功した場合、実装は以下を満たさなければならない。

1. 新しいフェッチ回数を 1 増やして確定する。
2. `repolist/<count>/db.yaml` を出力する。
3. `fetch.yaml` に `<count>: <timestamp>` を追加または更新する。

更新順は、利用者から見て「`fetch.yaml` に記録されている回数に対して、対応する `db.yaml` が存在する」状態になることを保証しなければならない。

### 5.2 `fix` 実行時

`fix` は、ユーザディレクトリ配下を再帰的に検査し、以下の整合性を回復する。

1. 空ディレクトリを残さない。
2. `repolist` 直下の数値ディレクトリ名の最大値を求める。
3. `fetch.yaml` にその最大値のエントリが存在しない場合は追加する。
4. `fetch.yaml` に存在する最大キーが、上記最大値より大きい場合は修正する。

補足:

- `fix` は既存の `db.yaml` 内容を書き換えない。
- `fix` は `fetch.yaml` の値として使うタイムスタンプを再構成できない場合、対象エントリの値に「既存最大エントリの値」または実行時刻を用いる実装を許容する。ただし採用した補完規則は固定でなければならない。
- 数値ディレクトリではない名前は、`fix` の回数算出対象に含めない。

### 5.3 削除規則

- `fix` は空ディレクトリのみ削除してよい。
- `db.yaml` を含むディレクトリ、または非空ディレクトリは削除してはならない。
- `fetch.yaml` の既存エントリは、最大値整合のために必要な場合を除き削除してはならない。

## 6. 公開クラス仕様

## 6.1 `Clix`

責務:

- `ghrepo` CLI のサブコマンドとオプションを定義する。

### コンストラクタ

```python
Clix(description: str, command_dict: dict[str, Any]) -> None
```

事前条件:

- `command_dict` は少なくとも `setup`, `list`, `fix` の各キーを持つ。

事後条件:

- `setup`, `list`, `fix` の各サブコマンドが利用可能になる。

### `fix` サブコマンド仕様

コマンド形式:

```text
ghrepo fix [--user USER] [--verbose]
```

引数:

- `--user`
  - 対象ユーザ名。
  - 未指定時は認証済み GitHub ユーザを正規化した値を使用する。
- `--verbose`
  - 修復前後の要約情報を標準出力に表示する。

動作:

- 対象ユーザディレクトリ配下の保存構造を検査する。
- 空ディレクトリを再帰的に削除する。
- `fetch.yaml` と `repolist` の最大回数を整合させる。

## 6.2 `Ghrepo`

責務:

- CLI サブコマンドごとに `AppStore` 初期化とコマンド実行を仲介する。

### `main`

```python
main() -> None
```

仕様:

- 引数を解析し、選択されたサブコマンドに対応する関数を呼び出す。
- `fix` が指定された場合は `Ghrepo.fix_repos(args)` を呼び出す。

### `fix_repos`

```python
@classmethod
def fix_repos(cls, args: argparse.Namespace) -> None
```

引数:

- `args.user`
- `args.verbose`

処理概要:

1. 対象ユーザの `AppStore` を初期化する。
2. `CommandList` を生成する。
3. `CommandList.fix_storage(...)` を呼び出す。
4. 必要に応じて修復結果を表示する。

副作用:

- 対象ユーザディレクトリ配下の空ディレクトリを削除する。
- `fetch.yaml` を更新する。

例外・失敗時:

- ユーザディレクトリが作成できない、または読み書きできない場合は失敗とする。
- YAML 読み込みに失敗した場合は、原因を利用者に通知して異常終了する。

## 6.3 `CommandList`

責務:

- `gh repo list` 実行コマンドの構築
- 取得結果のスナップショット化
- `fetch.yaml` と `repolist/<count>/db.yaml` の整合的な更新
- `fix` サブコマンドによる保存構造の修復

### コンストラクタ

```python
CommandList(appstore: AppStore, json_fields: list[str], user: str | None) -> None
```

意味:

- `appstore` は対象ユーザディレクトリに結びついた永続化コンテキストである。
- `json_fields` は `gh repo list --json` に渡すフィールド一覧である。
- `user` は CLI で明示指定されたユーザ名である。`None` または空文字列の場合は設定値を用いる。

### `get_command_for_project`

```python
def get_command_for_project(self, args: argparse.Namespace) -> str
```

仕様:

- `gh repo list` に渡す完全なコマンド文字列を返す。
- 戻り値には、少なくとも `--json` が含まれる。
- 対象ユーザが現在ユーザと異なる場合は `--user` を含める。
- 取得上限を適用する場合は `--limit` を含める。

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
- 返却される各要素には `count`, `valid`, `field_1`, `field_2`, `field_3` を付与する。
- 返却結果は、当該回数の `db.yaml` に保存可能な形式でなければならない。

### `save_snapshot`

```python
def save_snapshot(
    self,
    count: int,
    timestamp: str,
    assoc: dict[str, dict[str, Any]],
) -> None
```

新規公開メソッド。

仕様:

- `repolist/<count>/db.yaml` を出力する。
- `fetch.yaml` に `<count>: <timestamp>` を反映する。
- 呼び出し成功後、`fetch.yaml` と `repolist/<count>/db.yaml` は整合した状態で存在しなければならない。

### `fix_storage`

```python
def fix_storage(self, verbose: bool = False) -> dict[str, Any]
```

新規公開メソッド。

戻り値:

- 修復結果の要約辞書。

戻り値の必須キー:

- `removed_empty_directories`: `int`
- `max_repolist_count`: `int | None`
- `fetch_updated`: `bool`
- `warnings`: `list[str]`

処理概要:

1. ユーザディレクトリ配下を再帰走査する。
2. 空ディレクトリを削除する。
3. `repolist` 直下の数値ディレクトリ名を収集する。
4. 最大値に基づいて `fetch.yaml` を補正する。
5. 実施内容を要約して返す。

例外・失敗時:

- `fetch.yaml` が YAML として不正なら例外を送出してよい。
- `repolist` 不在時は警告付きで空集合として扱ってよい。

## 7. 独立関数仕様

本仕様では、以下の独立関数を公開してよい。
いずれも `CommandList.fix_storage()` の補助として利用する。

### `remove_empty_directories`

```python
def remove_empty_directories(root_dir: str) -> int
```

仕様:

- `root_dir` 配下を葉から順に走査し、空ディレクトリを削除する。
- 削除したディレクトリ数を返す。
- 非空ディレクトリは削除しない。

### `collect_repolist_counts`

```python
def collect_repolist_counts(repolist_dir: str) -> list[int]
```

仕様:

- `repolist_dir` 直下のディレクトリ名のうち、正の整数に解釈できるものだけを昇順で返す。
- `0`、負数、数値以外の名前は無視する。

### `normalize_fetch_assoc`

```python
def normalize_fetch_assoc(
    fetch_assoc: dict[int, str],
    repolist_counts: list[int],
    fallback_timestamp: str,
) -> tuple[dict[int, str], bool]
```

仕様:

- `repolist_counts` の最大値が `fetch_assoc` に存在し、かつ最大キーになるように補正する。
- 補正後の連想配列と、変更有無を返す。
- 補正時に新規エントリの値が必要で、既存値を流用できない場合は `fallback_timestamp` を用いる。

## 8. 正常系の動作要約

### 8.1 `ghrepo list`

1. ユーザを確定する。
2. `gh repo list` を実行する。
3. 新しい回数を採番する。
4. `repolist/<count>/db.yaml` を保存する。
5. `fetch.yaml` を更新する。

### 8.2 `ghrepo fix`

1. ユーザを確定する。
2. 空ディレクトリを削除する。
3. `repolist` の最大回数を求める。
4. `fetch.yaml` を補正する。
5. 必要に応じて要約を表示する。

## 9. 異常系

- GitHub CLI 実行失敗時は、新しいフェッチ回数を確定してはならない。
- `db.yaml` 保存失敗時は、対応する `fetch.yaml` エントリだけが残る状態にしてはならない。
- `fix` 実行中に一部の空ディレクトリ削除に失敗しても、継続可能な範囲では処理継続を許容する。ただし警告を返すこと。
- `fetch.yaml` が存在しない場合、`fix` は空の YAML 連想配列として再生成してよい。

## 10. 非対象

- `db.yaml` の各リポジトリ項目の詳細スキーマ拡張
- リポジトリ一覧の差分表示 UI
- 壊れた `db.yaml` 内容の自動修復
