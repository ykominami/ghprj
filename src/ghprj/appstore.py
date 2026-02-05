import os
import sys
from pathlib import Path
from typing import Any

from ghprj.storex import Storex


class AppStore:
  def __init__(self, prog_name: str) -> None:
    self.prog_name = prog_name
    self.file_type = "yaml"

    if sys.platform == "win32":
      # Windows: APPDATA / LOCALAPPDATA
      config_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
      data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
      config_file_name_array = [str(config_dir), prog_name, file_name]
      db_file_name_array = [str(data_dir), prog_name, file_name]
    else:
      # Linux/macOS: XDG規約
      home_path = Path.home()
      config_file_name_array = [str(home_path), ".config", prog_name, file_name]
      db_file_name_array = [str(home_path), ".local", "share", prog_name, file_name]

    self.config_file = Storex(self.file_type, config_file_name_array)
    self.db_file = Storex(self.file_type, db_file_name_array)

  def get_from_config(self, key: str) -> Any:
    return self.config_file.get(key)

  def get_from_db(self, key: str) -> Any:
    return self.db_file.get(key)

  def output_config(self, data: dict[str, Any]) -> None:
    self.config_file.output(data)

  def output_db(self, data: dict[str, Any]) -> None:
    self.db_file.output(data)
