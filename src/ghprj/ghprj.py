"""コマンドライン実行ユーティリティ"""

import json
import subprocess
from pathlib import Path
from typing import Any, Optional, cast

from ghprj.cli import Cli


class Ghprj:
    """GitHub リポジトリメタデータ抽出・変換ユーティリティクラス"""

    def __init__(self) -> None:
        """Ghprjインスタンスを初期化する"""
        pass

    def run_command(
        self,
        command: str | list[str],
        shell: bool = False,
        encoding: str = "utf-8",
        timeout: Optional[int] = None,
    ) -> tuple[str, int]:
        """
        コマンドラインを実行して、標準出力への出力を文字列として受け取る。

        Args:
            command: 実行するコマンド（文字列またはリスト）
            shell: shell経由で実行するかどうか（デフォルト: False）
            encoding: 出力のエンコーディング（デフォルト: utf-8）
            timeout: タイムアウト秒数（デフォルト: None）

        Returns:
            (標準出力の文字列, 終了コード) のタプル

        Raises:
            subprocess.TimeoutExpired: タイムアウトが発生した場合
            subprocess.SubprocessError: その他のサブプロセスエラー

        Example:
            >>> ghprj = Ghprj()
            >>> output, return_code = ghprj.run_command("echo hello")
            >>> print(output)  # "hello\\n"
            >>> print(return_code)  # 0
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                encoding=encoding,
                timeout=timeout,
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired as e:
            timeout_float = float(timeout) if timeout is not None else float(0)
            raise subprocess.TimeoutExpired(
                cmd=command,
                timeout=timeout_float,
                output=e.stdout.decode(encoding) if e.stdout else "",
                stderr=e.stderr.decode(encoding) if e.stderr else "",
            )
        except subprocess.SubprocessError:
            raise

    def run_command_simple(self, command: str | list[str], shell: bool = False) -> str:
        """
        コマンドラインを実行して、標準出力への出力を文字列として受け取る（シンプル版）。
        エラー時は例外を発生させる。

        Args:
            command: 実行するコマンド（文字列またはリスト）
            shell: shell経由で実行するかどうか（デフォルト: False）

        Returns:
            標準出力の文字列

        Raises:
            subprocess.CalledProcessError: コマンドが非ゼロの終了コードで終了した場合

        Example:
            >>> ghprj = Ghprj()
            >>> output = ghprj.run_command_simple("echo hello")
            >>> print(output)  # "hello\\n"
        """
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout

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

    def array_to_dict(
        self, data: list[dict[str, Any]], key: str
    ) -> dict[str, dict[str, Any]]:
        """
        JSON形式文字列の配列から、指定文字列をキーとする連想配列に変換する。

        Args:
            data: 辞書のリスト（JSON配列をパースしたもの）
            key: 連想配列のキーとして使用するフィールド名

        Returns:
            指定したキーをキーとし、元の要素を値とする連想配列（辞書）

        Raises:
            KeyError: 指定したキーが要素に存在しない場合
            TypeError: 要素が辞書でない場合

        Example:
            >>> ghprj = Ghprj()
            >>> data = [
            ...     {"name": "repo1", "url": "https://example.com/repo1"},
            ...     {"name": "repo2", "url": "https://example.com/repo2"}
            ... ]
            >>> result = ghprj.array_to_dict(data, "name")
            >>> print(result["repo1"])  # {"name": "repo1", "url": "https://example.com/repo1"}
        """
        result: dict[str, dict[str, Any]] = {}
        for item in data:
            if not isinstance(item, dict):
                raise TypeError(
                    f"配列の要素は辞書である必要があります。現在の型: {type(item).__name__}"
                )
            if key not in item:
                raise KeyError(
                    f"キー '{key}' が要素に存在しません。要素のキー: {list(item.keys())}"
                )
            key_value = item[key]
            if not isinstance(key_value, (str, int, float, bool)) or key_value is None:
                raise ValueError(
                    f"キー '{key}' の値は文字列、数値、真偽値である必要があります。現在の型: {type(key_value).__name__}"
                )
            result[str(key_value)] = item
        return result

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
    command = 'gh repo list --limit 400 --json name,url,owner,nameWithOwner,parent,pullRequests,createdAt,description,diskUsage,hasProjectsEnabled,homepageUrl -q " .  '
    repo_json_file = "repos.json"
    repo_tsv_file = "repos.tsv"
    out_dir = "_output"
    out_path = Path(out_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)

    ghprj = Ghprj()
    cli = Cli()
    args = cli.get_args()
    repo_json_file_path = out_path / repo_json_file
    if repo_json_file_path.exists() and not args.f:
        data = cast(list[dict[str, Any]], ghprj.load_json_array(repo_json_file_path))
    else:
        raw = ghprj.run_command_simple(command)
        ghprj.save_file(raw, repo_json_file)
        data = cast(list[dict[str, Any]], json.loads(raw))
    repo_tsv_path = out_path / repo_tsv_file
    # repo_dict = ghprj.array_to_dict(data, "name")
    # print(len(repo_dict))
    tsv = ghprj.array_to_tsv(
        data,
        [
            "isPrivate",
            "name",
            "url",
            "owner",
            "nameWithOwner",
            "parent",
            "pullRequests",
            "createdAt",
            "description",
            "diskUsage",
            "hasProjectsEnabled",
            "homepageUrl",
        ],
    )

    ghprj.save_file(tsv, str(repo_tsv_path))

    items = tsv.split("\n")
    headers_line, *rows = items
    heads = headers_line.split("\t")
    # print(heads)
    # print(rows[0])
    for item in rows:
        fields = item.split("\t")
        assoc = {x: y for x, y in zip(heads, fields)}
        print(assoc)
        # array = [[x,y] for x, y in zip(heads, fields)]
        # print(array)


    '''
        item = item.split("\t")
        print(item)
        name = item[0]
        url = item[1]
        owner = item[2]
        nameWithOwner = item[3]
        parent = item[4]
        pullRequests = item[5]
        createdAt = item[6]
        description = item[7]
        diskUsage = item[8]
        hasProjectsEnabled = item[9]
        homepageUrl = item[10]
    '''
