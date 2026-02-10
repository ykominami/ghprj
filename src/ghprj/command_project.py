import argparse
import json
from hmac import new

from ghprj.appstore import AppStore
from ghprj.command import Command
from ghprj.appconfig import AppConfig
from ghprj.timex import Timex


class CommandProject(Command):
    def __init__(self, appstore: AppStore, json_fields: [str]) -> None:
        self.appstore = appstore
        self.json_fields = json_fields
        self.user = self.appstore.get_from_config("config", "USER")

    def get_command_for_project(self, args: argparse.Namespace) -> str:
        user_option = ""
        if args.user is None or args.user == "" or args.user == self.user:
            limit_value = 400
            limit_option = f"--limit {limit_value}"
        else:
            if args.user != "":
                user_option = f"--user {args.user}"

        if args.json is None:
            json_value = ",".join(self.json_fields)
            json_option = f"--json {json_value}"
        else:
            json_option = f"--json {args.json}"

        command = f"gh repo list {limit_option} {json_option} {user_option}"
        print(command)
        return command

    def get_next_count(self, fetch_assoc: dict[int, str]) -> dict[int, str]:
        if fetch_assoc is None:
            num = 1
            fetch_assoc = {num: ""}
            next_count = num
        else:
            num = 0
            for item in fetch_assoc:
                item_num = int(item)
                if item_num > num:
                    num = item_num

            next_count = num + 1
            fetch_assoc[next_count] = Timex.get_now()

        return [next_count, fetch_assoc]

    def isUpdated(self, old_item: dict[str, str], new_item: dict[str, str]) -> bool:
        for key in AppConfig.default_json_fields:
            if old_item[key] != new_item[key]:
                return True
        return False

    def update(
        self, old_assoc: dict[str, dict[str, str]], assoc: dict[str, dict[str, str]]
    ) -> dict[str, dict[str, str]]:
        new_assoc = {}

        assoc_names = list(assoc.keys())
        old_assoc_names = list(old_assoc.keys())
        for old_assoc_name in old_assoc_names:
            if old_assoc_name in assoc_names:
                old_item = old_assoc[old_assoc_name]
                new_item = assoc[old_assoc_name]
                if self.isUpdated(old_item, new_item):
                    new_assoc[old_assoc_name] = new_item
                else:
                    new_assoc[old_assoc_name] = old_item

                assoc_names.remove(old_assoc_name)
            else:
                new_assoc[old_assoc_name] = old_item

        for remain_assoc_name in assoc_names:
            item = assoc[remain_assoc_name]
            item["valid"] = True
            new_assoc[remain_assoc_name] = item

        return new_assoc

    def all_project(
        self, args: argparse.Namespace, appstore: AppStore, count: int
    ) -> str:
        # fetch_assoc = self.appstore.assoc['db']['fetch']['value']

        command_line = self.get_command_for_project(args)
        json_str = self.run_command_simple(command_line)
        json_array = json.loads(json_str)
        assoc = self.array_to_dict(json_array, "name")
        for name, item in list(assoc.items()):
            item["count"] = count
            item["valid"] = True
            assoc[name] = item

        old_assoc = appstore.get_assoc_from_db("db")
        new_assoc = self.update(old_assoc, assoc)
        appstore.output_db("db", new_assoc)
        return assoc
