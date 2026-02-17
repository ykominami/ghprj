import argparse
import json
from hmac import new

# from ghprj.appstore import AppStore
from yklibpy.db.appstore import AppStore
# from ghprj.command import Command
from yklibpy.command import Command
from yklibpy.config.appconfig import AppConfig
#from ghprj.timex import Timex
from yklibpy.common.timex import Timex


class CommandRepo(Command):
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
        # print(command)
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

    class UpdateInfo:
        def make_item(self, diff: bool, key: str, old_value: str, new_value: str):
            return {
                'diff': diff,
                'key': key,
                'old_value':old_value,
                'new_value': new_value
            }

        def __init__(self):
            self.item_array: list[dict[str, str]] = []

        def add_item(self, diff: bool, key: str, old_value: str, new_value: str):
            self.item_array.append(self.make_item(diff, key, old_value, new_value))

        def get_result(self) -> bool:
            for item in self.item_array:
                if item['diff']:
                    return True
            return False

        def get_item_array(self) -> list[dict[str, str]]:
            return self.item_array

    def isUpdated(self, name: str,old_item: dict[str, str], new_item: dict[str, str]) -> bool:
        updateinfo = self.UpdateInfo()
        for key in AppConfig.default_json_fields:
            old_value = old_item[key]
            new_value = new_item[key]
            if old_item[key] != new_item[key]:
                diff = True
            else:
                diff = False
            updateinfo.add_item(diff, key, old_value, new_value)
        item_array = updateinfo.get_item_array()
        result = updateinfo.get_result()
        # print(f'isUpdated name={name} result={result} { json.dumps(item_array, indent=2) }')
        print(f'isUpdated name={name}')
        return updateinfo.get_result()

    def update(
        self, old_assoc: dict[str, dict[str, str]], assoc: dict[str, dict[str, str]]
    ) -> dict[str, dict[str, str]]:
        #
        new_assoc = {}

        assoc_names = list(assoc.keys())
        old_assoc_names = list(old_assoc.keys())
        for old_assoc_name in old_assoc_names:
            if old_assoc_name in assoc_names:
                old_item = old_assoc[old_assoc_name]
                new_item = assoc[old_assoc_name]
                result = self.isUpdated(old_assoc_name, old_item, new_item)
                print(f'U old_assoc_name={old_assoc_name} result={result}')
                if result:
                    new_assoc[old_assoc_name] = new_item
                    print(f'U-T new_assoc[old_assoc_name][count]={new_assoc[old_assoc_name]['count']}')
                    # breakpoint()
                else:
                    new_assoc[old_assoc_name] = old_item
                    print(f'U-F old_assoc[old_assoc_name][count]={old_assoc[old_assoc_name]['count']}')
                    # breakpoint()
                assoc_names.remove(old_assoc_name)
            else:
                new_assoc[old_assoc_name] = old_item

        for remain_assoc_name in assoc_names:
            item = assoc[remain_assoc_name]
            item["valid"] = True
            new_assoc[remain_assoc_name] = item

        return new_assoc

    def get_all_repos(
        self, args: argparse.Namespace, appstore: AppStore, count: int
    ) -> str:
        command_line = self.get_command_for_project(args)
        json_str = self.run_command_simple(command_line)
        json_array = json.loads(json_str)
        assoc = self.array_to_dict(json_array, "name")
        for name, item in list(assoc.items()):
            item["count"] = count
            item["valid"] = True
            item["field_1"] = ''
            item["field_2"] = ''
            item["field_3"] = ''
            assoc[name] = item

        old_assoc = appstore.get_assoc_from_db("db")
        new_assoc = self.update(old_assoc, assoc)
        '''
        for new_name in list(new_assoc.keys()):
            new_item = new_assoc[new_name]
            count_v = 'count'
            print(f'new_name={new_name} new_assoc[new_name][{count_v}]={new_assoc[new_name][count_v]}')
        '''

        return new_assoc
