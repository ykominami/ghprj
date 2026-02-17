import argparse
from typing import Any
from yklibpy.cli import Cli

class Clix:
    def __init__(self, description: str, command_dict: dict[str, Any]) -> None:
        self.cli = Cli(description)

        self.parser = self.cli.get_parser()

        subparsers = self.cli.get_subparsers('command')

        # サブコマンド "setup"
        p_setup = subparsers.add_parser("setup", help="Setup for config file")
        # setup()
        p_setup.set_defaults(func=command_dict['setup'])
        p_setup.add_argument("--user", help="GitHub user name")

        # サブコマンド "list"
        p_list = subparsers.add_parser("list", help="list all repositorie)s")
        p_list.set_defaults(func=command_dict['list'])

        p_list.add_argument("-f", action="store_true", help="force download")
        p_list.add_argument("-v", action="store_true", help="verbose")
        p_list.add_argument("--user", help="GitHub user name")
        p_list.add_argument("--limit", type=int, help="limit the number of repos")
        p_list.add_argument("--json", type=str, help="json output")
        default_output_file = "repos.json"
        p_list.add_argument(
            "--output", default=default_output_file, help="Output file name"
        )

    def get_subparsers(self) -> argparse.ArgumentParser:
        return self.cli.get_subparsers()

    def parse_args(self) -> argparse.Namespace:
        return self.cli.parse_args()

