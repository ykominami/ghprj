"""コマンドライン実行ユーティリティ"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional, cast

from dotenv import load_dotenv

from ghprj.cli import Cli


def run_command(
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
        >>> output, return_code = run_command("echo hello")
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


def run_command_simple(command: str | list[str], shell: bool = False) -> str:
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
        >>> output = run_command_simple("echo hello")
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


def load_json_array(file_path: str | Path, encoding: str = "utf-8") -> list[Any]:
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
        >>> data = load_json_array("repos.json")
        >>> print(len(data))  # 配列の要素数
        >>> print(data[0])  # 最初の要素
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"JSONファイルは配列形式である必要があります。現在の型: {type(data).__name__}")
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSONのパースに失敗しました: {e.msg}", e.doc, e.pos)

def save_as_json(data: list[Any], file_path: str, encoding: str = "utf-8") -> None:
    with open(file_path, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_file(data: str, file_path: str | Path, encoding: str = "utf-8") -> None:
    with open(file_path, "w", encoding=encoding) as f:
        f.write(data)


def array_to_dict(data: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
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
        >>> data = [
        ...     {"name": "repo1", "url": "https://example.com/repo1"},
        ...     {"name": "repo2", "url": "https://example.com/repo2"}
        ... ]
        >>> result = array_to_dict(data, "name")
        >>> print(result["repo1"])  # {"name": "repo1", "url": "https://example.com/repo1"}
    """
    result: dict[str, dict[str, Any]] = {}
    for item in data:
        if not isinstance(item, dict):
            raise TypeError(f"配列の要素は辞書である必要があります。現在の型: {type(item).__name__}")
        if key not in item:
            raise KeyError(f"キー '{key}' が要素に存在しません。要素のキー: {list(item.keys())}")
        key_value = item[key]
        if not isinstance(key_value, (str, int, float, bool)) or key_value is None:
            raise ValueError(f"キー '{key}' の値は文字列、数値、真偽値である必要があります。現在の型: {type(key_value).__name__}")
        result[str(key_value)] = item
    return result


def array_to_tsv(data: list[dict[str, Any]], headers: Optional[list[str]] = None) -> str:
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
        >>> data = [
        ...     {"name": "repo1", "url": "https://example.com/repo1", "stars": 100},
        ...     {"name": "repo2", "url": "https://example.com/repo2", "stars": 200}
        ... ]
        >>> tsv = array_to_tsv(data)
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
            raise TypeError(f"配列の要素は辞書である必要があります。現在の型: {type(item).__name__}")
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

def get_option(
    args: Any, default_json_fields: list[str] | None = None
) -> list[str]:
    user_value = args.user
    print(f'user_value: {user_value}')
    if user_value is None:
        user_option = ""
    else:
        user_option = user_value

    limit_option: str
    limit_value = args.limit
    if limit_value is None:
        if user_value is not None:
            if user_value == "ykominami":
                limit_value = 400
        else:
            limit_value = 400

    if limit_value is None:
        limit_option = ""
    else:
        limit_option = f"--limit {limit_value}"

    print(f'limit_option: {limit_option}')
    json_value = args.json
    if json_value is not None:
        json_option = f"--json {json_value}"
    elif default_json_fields:
        json_option = f"--json {','.join(default_json_fields)}"
    else:
        json_option = ""

    print(f'json_option: {json_option}')

    return [user_option, limit_option, json_option]

def main() -> None:
    load_dotenv()
    repo_json_file = os.environ.get("REPO_JSON_FILE", "repos.json")
    repo_tsv_file = os.environ.get("REPO_TSV_FILE", "repos.tsv")
    out_dir = os.environ.get("OUTPUT_DIR", "_output")

    cli = Cli()
    args = cli.get_args()
    if args.setup:
        cli.setup()
        return

    # デフォルトのJSONフィールドがない場合はフォールバック
    default_json_fields = cli.default_json_fields
    if not default_json_fields:
        default_json_fields = [
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
        ]
    [user_option, limit_option, json_option] = get_option(args, default_json_fields)
    command = f'gh repo list {user_option} {limit_option} {json_option} '
    print(f'command: {command}')

    out_path = Path(out_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)

    # --output引数が指定されていればそちらを使用
    if args.output:
        repo_json_file = args.output

    repo_json_file_path = out_path / repo_json_file
    if repo_json_file_path.exists() and not args.f:
        data = cast(list[dict[str, Any]], load_json_array(repo_json_file_path))
    else:
        raw = run_command_simple(command)
        # print(f'raw: {raw}')
        data = cast(list[dict[str, Any]], json.loads(raw))
        save_file(raw, repo_json_file_path)
    repo_tsv_path = out_path / repo_tsv_file
    # repo_dict = array_to_dict(data, "name")
    # print(len(repo_dict))
    '''
    tsv_headers = ["isPrivate", "name", "url", "owner", "nameWithOwner", "parent", "pullRequests", "createdAt", "description", "diskUsage", "hasProjectsEnabled", "homepageUrl"]
    '''
    if args.json is None:
        tsv_headers = cli.default_json_fields
    else:
        tsv_headers = args.json.split(",")

    data_sorted = sorted(data, key=lambda x: x.get("createdAt", ""), reverse=True)
    tsv_sorted = array_to_tsv(data_sorted, tsv_headers)

    save_file(tsv_sorted, str(repo_tsv_path))

    if args.v:
        for item in data_sorted:
            print(f'{item["name"]} {item["createdAt"]}')
