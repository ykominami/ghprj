# AppConfigx 外部仕様書

## 概要

`ghrepo` パッケージ固有の設定値・フィールド定義を集約するクラス。  
`yklibpy.config.appconfig.AppConfig` を継承し、ファイル種別マップ、ファイル関連付け辞書、デフォルト JSON フィールドリストを提供する。

**モジュール:** `ghrepo.appconfigx`  
**基底クラス:** `yklibpy.config.appconfig.AppConfig`

---

## クラス変数

### `BASE_NAME_SNAPSHOTS: ClassVar[str]`

`snapshots` — スナップショット作成記録ファイル (`snapshots.yaml`) の基本名。

### `BASE_NAME_REPOS: ClassVar[str]`

`repos` — リポジトリ一覧ファイル (`repos.yaml`) の基本名。`AppStore` の DB 登録名（内部キー `"repos"` と対応）。

### `SNAPSHOT_TOP_DIR_NAME: ClassVar[str]`

`snapshots` — スナップショットトップディレクトリ名。

### `file_type_dict: ClassVar[dict[str, str]]`

ファイル種別キーと拡張子のマッピング。

| キー | 値 |
|---|---|
| `FILE_TYPE_YAML` | `.yaml` |
| `FILE_TYPE_JSON` | `.json` |
| `FILE_TYPE_TOML` | `.toml` |

### `file_assoc: ClassVar[dict[str, dict[str, dict[str, Any]]]]`

ファイル種別・ファイル名・属性のネスト辞書。  
`AppStore` が設定ファイルと DB ファイルのパス解決に使用する。

```
KIND_CONFIG
  └─ config.yaml (FILE_TYPE_YAML)
KIND_DB
  ├─ repos.yaml  (FILE_TYPE_YAML)
  └─ snapshots.yaml (FILE_TYPE_YAML)
```

### `default_json_fields_in_db: ClassVar[list[str]]`

DB に保存する際のフィールド一覧（管理フィールドを含む）。

| フィールド | 用途 |
|---|---|
| `name` | リポジトリ名 |
| `snapshot-id` | スナップショット番号（管理フィールド） |
| `valid` | 有効フラグ（管理フィールド） |
| `field_1` / `field_2` / `field_3` | ユーザー注釈用（管理フィールド） |
| `visibility` | 公開設定 |
| `url` | リポジトリ URL |
| `owner` | オーナー情報 |
| `nameWithOwner` | オーナー込みリポジトリ名 |
| `parent` | 親リポジトリ情報 |
| `pullRequests` | PR 集計情報 |
| `createdAt` | 作成日時 |
| `description` | 説明文 |
| `diskUsage` | ディスク使用量 |
| `hasProjectsEnabled` | プロジェクト有効フラグ |
| `homepageUrl` | ホームページ URL |

### `default_json_fields: ClassVar[list[str]]`

`gh repo list --json` へ渡すデフォルトフィールド一覧（管理フィールドを除く）。  
`default_json_fields_in_db` から `snapshot-id`, `valid`, `field_1/2/3` を除いた 12 フィールド。

### `key: ClassVar[str]`

`"JSON_FIELDS"` — コンフィグファイル内でフィールドリストを参照するためのキー名。

---

## 継承元

`AppConfig` が提供する以下の定数・メソッドをそのまま利用する。

- `FILE_TYPE_YAML / FILE_TYPE_JSON / FILE_TYPE_TOML`
- `KIND_CONFIG / KIND_DB`
- `BASE_NAME_CONFIG`
- `FILE_TYPE / EXT_NAME / PATH / VALUE`

---

## 利用箇所

| モジュール | 用途 |
|---|---|
| `command_list.py` | `BASE_NAME_SNAPSHOTS`, `BASE_NAME_REPOS` でストア取得 |
| `command_setup.py` | `BASE_NAME_REPOS`, `BASE_NAME_SNAPSHOTS` で初期 DB 出力 |
| `ghrepo.py` | `file_assoc`, `file_type_dict`, `key`, `default_json_fields` で `AppStore` 初期化 |
