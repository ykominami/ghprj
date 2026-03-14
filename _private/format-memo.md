このプロジェクトのフォーマット設定
CLAUDE.md に記載されている通り:
Formatter: Black（行長88文字）
Linter: Ruff（ルール E, F, I, N / E501は無視）
Type checker: MyPy strict モード
Python: 3.14
確認のため pyproject.toml を見てみます。

一般的なPythonフォーマット標準

1. PEP 8（公式スタイルガイド）
インデント: スペース4つ（タブ不可）
行長: 79文字（Black使用時は88文字が標準）
import順: 標準ライブラリ → サードパーティ → ローカル（空行で区切る）
命名: snake_case（関数/変数）、PascalCase（クラス）、UPPER_CASE（定数）

2. 主要フォーマッター比較
ツール	特徴
Black	opinionated、設定不要、行長88がデフォルト。このプロジェクトで採用
Ruff format	Blackとほぼ互換、Rustで高速。Ruff に統合されている
autopep8	PEP 8準拠に最小限の修正
YAPF	Google製、カスタマイズ性が高い

3. 現在の主流（2025-2026年）
Ruff がリンターとフォーマッターを1つに統合し、急速に普及しています。このプロジェクトでは Black + Ruff（リントのみ）の組み合わせですが、ruff format で Black を置き換える構成も一般的です。

4. このプロジェクトでの実行方法
# フォーマット
uv run black src/
# リント
uv run ruff check src/
# 型チェック
uv run mypy src/

要点: PEP 8 が公式標準、実務では Black（または Ruff format） で自動フォーマットするのが現在のデファクトスタンダードです。
