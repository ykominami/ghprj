import os
import sys
from pathlib import Path
from typing import Any
from ghprj.storex import Storex


class AppStore:
    def __init__(self, prog_name: str, assoc: dict[str, dict[str, str]]) -> None:
        self.home_path = Path.home()
        self.prog_name = prog_name
        self.assoc = assoc
        self.set_ext_name()

    def set_ext_name(self):
        for kind in self.assoc:
            for base_name in self.assoc[kind]:
                self.assoc[kind][base_name]["ext_name"] = Storex.get_ext_name(
                    self.assoc[kind][base_name]["file_type"]
                )

    def prepare_config_file_and_db_file(self):
        for kind in self.assoc:
            for base_name in self.assoc[kind]:
                file_item_assoc = self.assoc[kind][base_name]
                file = self.get_file(kind, base_name, file_item_assoc)
                self.assoc[kind][base_name]["file"] = file

        return self.assoc

    def load_file(self):
        for kind in self.assoc:
            for base_name in self.assoc[kind]:
                self.assoc[kind][base_name]["value"] = self.assoc[kind][base_name][
                    "file"
                ].load()

    def get_assoc_from_config(self, base_name: str) -> Any:
        return self.assoc["config"][base_name]["value"]

    def get_assoc_from_db(self, base_name: str) -> Any:
        return self.assoc["db"][base_name]["value"]

    def get_file(self, kind: str, base_name: str, assoc: dist[str, str]):
        file = ""
        if kind == "config":
            file = self.get_config_file(base_name, assoc)
        else:
            file = self.get_db_file(base_name, assoc)

        return file

    def get_config_file(self, key: str, assoc: dist[str, str]):
        if sys.platform == "win32":
            # Windows: APPDATA / LOCALAPPDATA
            file_name_array = self.get_config_file_for_win(key, assoc["ext_name"])
        else:
            # Linux/macOS: XDG規約
            file_name_array = self.get_config_file_for_unix(key, assoc["ext_name"])

        file = Storex(assoc["file_type"], file_name_array)
        return file

    def get_db_file(self, key: str, assoc: dist[str, str]):
        file_name_array = []
        if sys.platform == "win32":
            # Windows: APPDATA / LOCALAPPDATA
            file_name_array = self.get_db_file_for_win(key, assoc["ext_name"])
        else:
            # Linux/macOS: XDG規約
            file_name_array = self.get_db_file_for_unix(key, assoc["ext_name"])

        file = Storex(assoc["file_type"], file_name_array)
        return file

    def get_config_file_for_win(self, base_name: str, ext_name: str):
        config_top_dir = Path(
            os.environ.get("APPDATA", str(self.home_path / "AppData" / "Roaming"))
        )
        file_name = f"{base_name}{ext_name}"
        config_file_name_array = [str(config_top_dir), self.prog_name, file_name]
        return config_file_name_array

    def get_db_file_for_win(self, base_name: str, ext_name: str):
        data_top_dir = Path(
            os.environ.get("LOCALAPPDATA", str(self.home_path / "AppData" / "Local"))
        )
        file_name = f"{base_name}{ext_name}"
        db_file_name_array = [str(data_top_dir), self.prog_name, file_name]
        return db_file_name_array

    def get_config_file_for_unix(self, base_name: str, ext_name: str):
        file_name = f"{base_name}{ext_name}"
        config_file_name_array = [
            str(self.home_path),
            ".config",
            self.prog_name,
            file_name,
        ]
        return config_file_name_array

    def get_db_file_for_unix(self, base_name: str, ext_name: str):
        file_name = f"{base_name}{ext_name}"
        db_file_name_array = [
            str(self.home_path),
            ".local",
            "share",
            self.prog_name,
            file_name,
        ]
        return db_file_name_array

    def get_from_config(self, base_name: str, key: str) -> Any:
        return self.assoc["config"][base_name]["value"][key]

    def output_config(self, key: str, data: dict[str, Any]) -> None:
        self.assoc["config"][key]["file"].output(data)

    def output_db(self, key: str, data: dict[str, Any]) -> None:
        self.assoc["db"][key]["file"].output(data)
