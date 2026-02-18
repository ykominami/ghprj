# from ghprj.command import Command
from yklibpy.command.command import Command
from yklibpy.db.appstore import AppStore

from ghprj.command_user import CommandUser


class CommandSetup(Command):
  def __init__(self, appstore: AppStore):
    self.appstore = appstore

  def run(self, key: str, default_json_fields: list[str]) -> None:
      data = {key: default_json_fields, "USER": self.appstore.user}
      self.appstore.output_config("config", data)
      self.appstore.output_db("db", {})
      self.appstore.output_db("fetch", {})
