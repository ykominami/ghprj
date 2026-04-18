# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ghrepo` is a GitHub repository metadata extraction and management utility. It fetches repo info via the GitHub CLI (`gh`), stores versioned snapshots as YAML, and supports searching by visibility or name. Written in Python with Japanese docstrings/comments.

## Build & Development Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Build distribution
uv build

# Run the CLI (subcommand required)
uv run ghrepo setup [--user <username>]
uv run ghrepo list [-f] [-v] [--user <username>] [--limit <n>] [--json <fields>]
uv run ghrepo fix [--user <username>] [--verbose]
uv run ghrepo search {public,private,both,internal,latest10} [--name <substring>] [--user <username>]

# Run tests (note: tests/ directory is currently empty)
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run a single test file
uv run pytest tests/test_foo.py

# Lint
uv run ruff check src/

# Format
uv run black src/

# Type check (strict mode)
uv run mypy src/
```

## Architecture

The package lives in `src/ghrepo/`. The `Ghrepo` class in `ghrepo.py` is the top-level orchestrator; `__init__.py` re-exports `Ghrepo`, `main`, and `get_user`.

Two entry points are registered: `ghrepo` → `main()`, `get_user` → `get_user()` (outputs the normalized username via `Loggerx.debug`, not stdout — visible only at DEBUG log level).

**Subcommands (defined in `clix.py`, dispatched in `ghrepo.py`):**

| Subcommand | Key flags | Purpose |
|---|---|---|
| `setup` | `--user` | Initialize config file and empty DB for a user |
| `list` | `-f/--force`, `-v/--verbose`, `--user`, `--limit`, `--json` | Fetch repos via `gh repo list`, save snapshot + `repos.yaml`; `--json` accepts a comma-separated field list overriding the config `JSON_FIELDS` (`visibility` is always appended) |
| `fix` | `--user`, `--verbose` | Remove empty directories and reconcile `snapshots.yaml`; does **not** rebuild `repos.yaml` |
| `search` | `search_name` (positional), `--name`, `--user`, `--verbose` | Query latest snapshot; `search_name` ∈ `{public, private, both, internal, latest10}` — `both` = public + private combined; prints JSON array of repo **name** strings to stdout |

**Storage layout (per user, managed via `yklibpy.db.AppStore`):**
- `<userdir>/snapshots.yaml` — dict of `{snapshot-id: ISO-timestamp}` recording each fetch (スナップショット作成記録ファイル)
- `<userdir>/repos.yaml` — latest repo assoc (name → repo dict) (リポジトリ一覧ファイル); internal key `"repos"` = `AppConfigx.BASE_NAME_REPOS`
- `<userdir>/snapshots/<snapshot-id>/snapshot.yaml` — numbered YAML snapshots (リポジトリ一覧スナップショットファイル)

**Data enrichment during fetch:** each repo item from `gh repo list` has management fields added — `snapshot-id` (snapshot number), `valid` (always `True`), `field_1/2/3` (empty strings for user annotation). The `visibility` field is normalized to lowercase (`public`/`private`/`internal`); it is always included in `--json` fields even if not explicitly requested.

**`list` subcommand fetch logic (`Ghrepo.list_repos`):**
- Fetches when `--force` is set **or** `snapshots.yaml` does not yet exist; otherwise loads and displays the existing `repos.yaml`.
- `save_snapshot` writes in this order: ① `snapshots/<id>/snapshot.yaml` → ② `snapshots.yaml` → ③ `repos.yaml` (merge-update).

**Key modules:**
- `appconfigx.py` — `AppConfigx(AppConfig)` holding two field lists: `default_json_fields` (passed to `gh repo list --json`) and `default_json_fields_in_db` (superset including management fields `snapshot-id`, `valid`, `field_1/2/3`); config key `"JSON_FIELDS"`
- `command_list.py` — `CommandList`: fetch (`get_all_repos`), snapshot (`save_snapshot`), and storage reconciliation (`fix_storage`); internal helpers `_remove_empty_directories`, `_collect_snapshot_ids`, `_coerce_snapshots_record_assoc`, `_normalize_snapshots_record_assoc` are static methods. `_coerce_snapshots_record_assoc` only type-coerces keys/values; `_normalize_snapshots_record_assoc` additionally trims excess IDs and fills in a missing max-ID entry. `get_next_snapshot_id` takes the max of IDs found in both `snapshots.yaml` and actual snapshot directories, then adds 1. `fix_storage` returns a dict with `removed_empty_directories`, `max_snapshot_id`, `snapshots_record_updated`, `warnings`. Defines type aliases `RepoItem = dict[str, Any]` and `RepoAssoc = dict[str, RepoItem]`.
- `command_search.py` — `CommandSearch`: loads the latest `snapshot.yaml` and filters by visibility (`_filter_by_visibility`), recency (`_take_latest_n_by_created_at` for `latest10`), and name substring (`_filter_by_name_substring`). `SEARCH_KINDS` is a `ClassVar[frozenset[str]]` class variable. Also duplicates the same `RepoItem`/`RepoAssoc` type aliases.
- `command_setup.py` — `CommandSetup`: writes initial config and empty `repos.yaml`/`snapshots.yaml` files
- `clix.py` — `Clix` wraps `yklibpy.cli.Cli` to register all subparsers

**External dependency:** `yklibpy` is a local editable package at `../yklibpy` (declared in `pyproject.toml` under `[tool.uv.sources]`) providing `AppStore`, `Storex`, `AppConfig`, `Cli`, `Command`, `CommandGhUser`, `Util`, `Loggerx`.

**Note:** `CommandList` and `CommandSearch` both contain a `_collect_snapshot_ids` static method (identical logic) and duplicate `RepoItem`/`RepoAssoc` type aliases. Any refactor should keep this duplication or extract it into `yklibpy` — do not introduce a standalone free function or module-level constant in this package.

## Code Style & Tooling

- **Python target:** 3.14 (`.python-version` specifies 3.14.0)
- **Formatter:** Black, line length 88
- **Linter:** Ruff with rules E, F, I, N (E501 ignored — delegated to Black)
- **Type checker:** MyPy in strict mode
- **Build backend:** `uv_build`
- **Docstrings/comments:** Written in Japanese

## ドキュメントディレクトリ・ファイル構成
### docs/spec 外部仕様書ディレクトリ
  - [index.md](docs/spec/index.md) 仕様書インデックス
  - [AppConfigx.md](docs/spec/AppConfigx.md) クラスAppConfigx外部仕様書
  - [Clix.md](docs/spec/Clix.md) クラスClix外部仕様書
  - [CommandList.md](docs/spec/CommandList.md) クラスCommandList外部仕様書
  - [CommandSearch.md](docs/spec/CommandSearch.md) クラスCommandSearch外部仕様書
  - [CommandSetup.md](docs/spec/CommandSetup.md) クラスCommandSetup外部仕様書
  - [Ghrepo.md](docs/spec/Ghrepo.md) クラスGhrepo外部仕様書

### docs/req 要求仕様書ディレクトリ

## 用語の定義

- **ユーザ**: `gh auth login` で認証されたGitHubアカウント
- **コンフィグディレクトリ**: 
  - Windows: `%APPDATA%/ghrepo/`
  - Unix 系: `~/.config/ghrepo/`
- **コンフィグファイル**: `config.yaml` 
  (キー: `JSON_FIELDS`, `USER`)

- **ユーザディレクトリ**:
  - Windows: `%LOCALAPPDATA%/ghrepo/<user>/`
  - Unix 系: `~/.local/share/ghrepo/<user>/`

- **リポジトリ一覧ファイル**: `repos.yaml`（内部キー `"repos"` = `AppConfigx.BASE_NAME_REPOS`）
  - 各リポジトリ一覧スナップショットファイルを、古いものから、新しいものに順にマージする。新しいものに同一<repo-id>のレコードが存在した場合、レコード内容に相違があれば、新しいレコードで更新する。相違がなければ、更新しない。
  - フォーマット: リポジトリ一覧スナップショットファイルのフォーマットと同一

- **スナップショット作成記録ファイル**: `snapshots.yaml`
  - (フォーマット: `<スナップショットID>: <タイムスタンプ>`)
- **スナップショットトップディレクトリ**: `snapshots`
- **個別スナップショットディレクトリ**: <スナップショットID>
- **スナップショットID**: <スナップショットID>
  - スナップショットを作成する回数であり、1から始まる整数
- **リポジトリ一覧スナップショットファイル**: `snapshot.yaml`
  - フォーマット:
	- <repo-id>:
	  snapshot-id: <スナップショットID>
	  createdAt: '2018-04-30T07:27:49Z'
	  description: 「GitHubを使ったデプロイ自動化実践 | Schoo」のハンズオン用リポジトリ
	  diskUsage: 12
	  field_1: ''
	  field_2: ''
	  field_3: ''
	  hasProjectsEnabled: true
	  homepageUrl: https://schoo.jp/class/5029
	  name: 20180430-schoo
	  nameWithOwner: ykominami/20180430-schoo
	  owner:
		id: MDQ6VXNlcjEwNjE3OQ==
		login: ykominami
	  parent:
		id: MDEwOlJlcG9zaXRvcnkxMzEwMDA0OTE=
		name: 20180430-schoo
		owner:
		  id: MDQ6VXNlcjQzNjA2NjM=
		  login: ttskch
	  pullRequests:
		totalCount: 0
	  url: https://github.com/ykominami/20180430-schoo
	  valid: true
	  visibility: public

## ディレクトリ/ファイル定義
<コンフィグディレクトリ>
  <コンフィグファイル>

<ユーザディレクトリ>
  <リポジトリ一覧ファイル> (repos.yaml)
  <スナップショット作成記録ファイル>
  <スナップショットトップディレクトリ>
    <個別スナップショットディレクトリ>
      <リポジトリ一覧スナップショットファイル>

以上で規定したディレクトリ、ファイルのみを作成・利用してください。

ArchitectureのEntory Points以外は、機能をクラスのインスタンスメソッド、クラスメソッドとして実装し、独立した関数としては実装しないでください。
