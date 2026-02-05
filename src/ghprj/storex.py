import json
from pathlib import Path
from typing import Any

import yaml


class Storex:
  def __init__(self, file_type: str, file_name_array: list[str] | None = None):
    self.file_name_array = file_name_array or []
    self.file_type = file_type

    # file_name_arrayは完全なパス要素の配列（呼び出し元で構築済み）
    self.file_path = Path(*self.file_name_array) if self.file_name_array else Path()

    self.store: dict[str, Any] = {}
    if self.file_path.exists():
      with open(self.file_path, "r", encoding="utf-8") as f:
        if self.file_type == "yaml":
          self.store = yaml.safe_load(f) or {}
        elif self.file_type == "json":
          self.store = json.load(f)
        else:
          self.store = {"_lines": f.readlines()}

  def get(self, key: str) -> Any:
    return self.store.get(key)

  def output(self, data: Any) -> None:
    # 親ディレクトリが存在しない場合は作成
    self.file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(self.file_path, "w", encoding="utf-8") as f:
      if self.file_type == "yaml":
        yaml.dump(data, f, allow_unicode=True)
      elif self.file_type == "json":
        json.dump(data, f, ensure_ascii=False, indent=2)
      else:
        f.write(str(data))

