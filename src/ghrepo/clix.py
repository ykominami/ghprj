import argparse
from collections.abc import Callable

from yklibpy.cli import Cli

type CommandHandler = Callable[[argparse.Namespace], None]


class Clix:
    """`ghrepo` のサブコマンド定義を組み立てる CLI ラッパー。"""

    def __init__(
        self, description: str, command_dict: dict[str, CommandHandler]
    ) -> None:
        """主要サブコマンドを登録した `Cli` インスタンスを構築する。"""
        self.cli = Cli(description)

        subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = (
            self.cli.get_subparsers("command")
        )
        # サブコマンド "setup"
        p_setup: argparse.ArgumentParser = subparsers.add_parser(
            "setup", help="Setup for config file"
        )
        p_setup.set_defaults(func=command_dict["setup"])
        p_setup.add_argument("--user", help="GitHub user name")

        # サブコマンド "list"
        p_list: argparse.ArgumentParser = subparsers.add_parser(
            "list", help="list all repositorie)s"
        )
        p_list.set_defaults(func=command_dict["list"])

        p_list.add_argument(
            "-f", "--force", action="store_true", help="force download"
        )
        p_list.add_argument("-v", "--verbose", action="store_true", help="verbose")
        p_list.add_argument("--user", help="GitHub user name")
        p_list.add_argument("--limit", type=int, help="limit the number of repos")
        p_list.add_argument("--json", type=str, help="json output")

        # サブコマンド "fix"
        p_fix: argparse.ArgumentParser = subparsers.add_parser(
            "fix", help="fix stored repository snapshots"
        )
        p_fix.set_defaults(func=command_dict["fix"])
        p_fix.add_argument("--user", help="GitHub user name")
        p_fix.add_argument("--verbose", action="store_true", help="verbose")

        # サブコマンド "search"
        p_search: argparse.ArgumentParser = subparsers.add_parser(
            "search", help="search repositories from latest snapshot"
        )
        p_search.set_defaults(func=command_dict["search"])
        p_search.add_argument(
            "search_name",
            choices=["public", "private", "both","internal", "latest10"],
            help="search kind",
        )
        p_search.add_argument("--name", help="substring pattern for repository name")
        p_search.add_argument("--user", help="GitHub user name")
        p_search.add_argument("--verbose", action="store_true", help="verbose")

    def get_subparsers(
        self, name: str
    ) -> argparse._SubParsersAction[argparse.ArgumentParser]:
        """内部の `Cli` が保持する subparsers を返す。"""
        return self.cli.get_subparsers(name)

    def parse_args(self) -> argparse.Namespace:
        """登録済み定義に従って CLI 引数を解析する。"""
        return self.cli.parse_args()

