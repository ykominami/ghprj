import json
from pathlib import Path
from typing import Any, Optional, cast

"""コマンドライン実行ユーティリティ"""
from ghprj.appconfig import AppConfig
from ghprj.storex import Storex

from ghprj.cli import Cli
from ghprj.command_project import CommandProject
from ghprj.command_user import CommandUser
from ghprj.appstore import AppStore


class Ghprj:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    def __init__(self) -> None:
        """Ghprjインスタンスを初期化する"""
        pass

    def load_json_array(
        self, file_path: str | Path, encoding: str = "utf-8"
    ) -> list[Any]:
        """
        JSON形式ファイルを読み込み、連装配列として返す。

        Args:
            file_path: 読み込むJSONファイルのパス
            encoding: ファイルのエンコーディング（デフォルト: utf-8）

        Returns:
            JSONファイルの内容をパースした配列（リスト）

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            json.JSONDecodeError: JSONのパースに失敗した場合
            ValueError: JSONが配列形式でない場合

        Example:
            >>> ghprj = Ghprj()
            >>> data = ghprj.load_json_array("repos.json")
            >>> print(len(data))  # 配列の要素数
            >>> print(data[0])  # 最初の要素
        """
        try:
            with open(file_path, "r", encoding=encoding) as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError(
                        f"JSONファイルは配列形式である必要があります。現在の型: {type(data).__name__}"
                    )
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"JSONのパースに失敗しました: {e.msg}", e.doc, e.pos
            )

    def save_as_json(
        self, data: list[Any], file_path: str | Path, encoding: str = "utf-8"
    ) -> None:
        """
        データをJSON形式でファイルに保存する。

        Args:
            data: 保存するデータ（リスト）
            file_path: 保存先ファイルパス
            encoding: ファイルのエンコーディング（デフォルト: utf-8）
        """
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_file(
        self, data: str, file_path: str | Path, encoding: str = "utf-8"
    ) -> None:
        """
        文字列データをファイルに保存する。

        Args:
            data: 保存する文字列データ
            file_path: 保存先ファイルパス
            encoding: ファイルのエンコーディング（デフォルト: utf-8）
        """
        with open(file_path, "w", encoding=encoding) as f:
            f.write(data)

    def array_to_tsv(
        self, data: list[dict[str, Any]], headers: Optional[list[str]] = None
    ) -> str:
        """
        JSON形式文字列の配列から、ヘッダー付きTSVに変換する。

        Args:
            data: 辞書のリスト（JSON配列をパースしたもの）
            headers: 出力するヘッダーの順序（指定しない場合は全キーを自動収集）

        Returns:
            ヘッダー付きTSV形式の文字列

        Raises:
            TypeError: 要素が辞書でない場合

        Example:
            >>> ghprj = Ghprj()
            >>> data = [
            ...     {"name": "repo1", "url": "https://example.com/repo1", "stars": 100},
            ...     {"name": "repo2", "url": "https://example.com/repo2", "stars": 200}
            ... ]
            >>> tsv = ghprj.array_to_tsv(data)
            >>> print(tsv)
            name\turl\tstars
            repo1\thttps://example.com/repo1\t100
            repo2\thttps://example.com/repo2\t200
        """
        if not data:
            return ""

        # すべてのキーを収集
        all_keys: set[str] = set()
        for item in data:
            if not isinstance(item, dict):
                raise TypeError(
                    f"配列の要素は辞書である必要があります。現在の型: {type(item).__name__}"
                )
            all_keys.update(item.keys())

        # ヘッダーの決定
        if headers is None:
            headers = sorted(all_keys)
        else:
            # 指定されたヘッダーに存在しないキーがあれば追加
            missing_keys = all_keys - set(headers)
            if missing_keys:
                headers = headers + sorted(missing_keys)

        # TSVの生成
        lines: list[str] = []

        # ヘッダー行
        lines.append("\t".join(headers))

        # データ行
        for item in data:
            values: list[str] = []
            for header in headers:
                value = item.get(header, "")
                # 値の変換
                if value is None:
                    values.append("")
                elif isinstance(value, (dict, list)):
                    # 辞書やリストはJSON文字列に変換
                    values.append(json.dumps(value, ensure_ascii=False))
                elif isinstance(value, bool):
                    # 真偽値は文字列に変換
                    values.append(str(value))
                else:
                    # その他の値は文字列に変換（タブや改行はそのまま）
                    values.append(str(value))
            lines.append("\t".join(values))

        return "\n".join(lines)


def main() -> None:
    """CLIエントリポイント"""
    Storex.set_file_type_dict(AppConfig.file_type_dict)

    ghprj = Ghprj()
    appstore = AppStore("ghprj", AppConfig.file_assoc)
    appstore.prepare_config_file_and_db_file()

    cli = Cli(appstore, AppConfig.key)
    args = cli.get_args()

    if args.setup:
        cli.setup(AppConfig.key, AppConfig.default_json_fields)
        return

    cli.load_file()
    json_fields = cli.get_from_config("config", AppConfig.key)
    command = CommandProject(appstore, json_fields)

    fetch_assoc = appstore.get_assoc_from_db("fetch")
    [count, fetch_assoc] = command.get_next_count(fetch_assoc)
    appstore.output_db("fetch", fetch_assoc)

    assoc = command.all_project(args, appstore, count)
    appstore.output_db("db", assoc)


def get_user() -> None:
    command = CommandUser()
    user = command.get_user()
    print(user)
