import subprocess
from typing import Any, Optional


class Command:
    def __init__():
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
