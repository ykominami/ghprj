import json
import yaml
from pathlib import Path
from typing import Any

from ghprj.appconfig import AppConfig


class Storex:
    _file_type_dict: dict[str, str] = {}

    @classmethod
    def set_file_type_dict(cls, file_type_dict: dict[str, str]) -> None:
        cls._file_type_dict = file_type_dict

    @classmethod
    def get_ext_name(cls, file_type: str) -> str:
        return cls._file_type_dict[file_type]

    def __init__(self, file_type: str, file_name_array: list[str] | None = None):
        self.file_name_array = file_name_array or []
        self.file_type = file_type

        # file_name_arrayは完全なパス要素の配列（呼び出し元で構築済み）
        self.file_path = Path(*self.file_name_array) if self.file_name_array else Path()

        self.store: dict[str, str] = {}

    def load(self) -> dict[str, Any]:
        if self.file_path.exists():
            # print(f'file_path={self.file_path} load file_path={self.file_path}')
            with open(self.file_path, "r", encoding="utf-8") as f:
                if self.file_type == AppConfig.FILE_TYPE_YAML:
                    self.store = yaml.safe_load(f) or {}
                elif self.file_type == AppConfig.FILE_TYPE_JSON:
                    self.store = json.load(f)
                else:
                    self.store = {"_lines": f.readlines()}

        return self.store

    def output(self, data: Any) -> None:
        # 親ディレクトリが存在しない場合は作成
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            if self.file_type == AppConfig.FILE_TYPE_YAML:
                # print(f'Storex output yaml self.file_path={self.file_path} data')
                yaml.dump(data, f, allow_unicode=True)
            elif self.file_type == AppConfig.FILE_TYPE_JSON:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                f.write(str(data))
