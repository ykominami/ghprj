# 日本語 Docstring 外部仕様書

## 1. 目的

`src/ghrepo` 配下の Python ソースに対して、クラス定義、メソッド定義、関数定義の先頭へ配置する docstring の記述方針を統一する。

既存 docstring は追記ではなく置換を前提とし、各定義について役割、前提、戻り値、失敗条件が読み取れる状態を完成条件とする。

## 2. 対象

- `src/ghrepo/ghrepo.py`
- `src/ghrepo/command_list.py`
- `src/ghrepo/command_setup.py`
- `src/ghrepo/clix.py`
- `src/ghrepo/appconfigx.py`
- `src/ghrepo/__init__.py`

対象定義の種類は次のとおり。

- すべてのトップレベル `class`
- すべてのクラスメソッド、インスタンスメソッド、`__init__`
- すべてのトップレベル `def`

## 3. 記述ルール

- 日本語で記述する。ただしクラス名、メソッド名、関数名、引数名は英語識別子をそのまま用いる。
- PEP 257 ベースの簡潔な docstring とする。
- 1 行または短い 1〜3 段落で十分な定義は簡潔に記述する。
- 引数、戻り値、失敗条件の説明が複数必要な定義だけ Google style の `Args`、`Returns`、`Raises` を使う。
- 型の説明は型ヒントに任せ、docstring では意味、制約、前提、利用意図を書く。
- 実装手順の逐語説明ではなく、呼び出し側が知るべき振る舞いを優先する。

## 4. モジュール別の書き分け

### `ghrepo.py`

- CLI エントリポイント、ログ設定、`AppStore` 初期化の責務を区別して書く。
- `list_repos` と `fix_repos` は保存先更新や補助コマンド呼び出しの流れが分かる表現にする。

### `command_list.py`

- スナップショット保存、`fetch` 情報の正規化、`gh repo list` 実行の役割を明記する。
- 補助関数は「何を正規化するか」「どの条件を捨てるか」「何を返すか」を短く書く。

### `command_setup.py`

- 初期設定ファイルと DB ファイルを作る責務を簡潔に書く。
- `run` は既定ユーザー補完と出力対象の初期化が分かるようにする。

### `clix.py`

- `argparse` の薄いラッパーであり、各サブコマンド定義を束ねる責務を書く。
- `get_subparsers` と `parse_args` は委譲メソッドであることを簡潔に書く。

### `appconfigx.py`

- GitHub リポジトリ取得で使う既定 JSON フィールド群を保持する設定クラスであることを書く。

## 5. 完了条件

- 対象定義すべてに日本語 docstring がある。
- 既存 docstring は仕様に合わせた表現へ置換されている。
- 複雑な定義だけが Google style を使い、単純な定義では冗長な節を増やしていない。
- docstring が型ヒントの焼き直しになっていない。
- 編集したファイルで lint エラーを新規発生させていない。
