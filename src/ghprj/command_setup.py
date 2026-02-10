from ghprj.command import Command
from ghprj.appstore import AppStore
from ghprj.command_user import CommandUser

class CommandSetup(Command):
  def __init__(self, appstore: AppStore):
    self.appstore = appstore

  def run(self, key: str, default_json_fields: list[str]) -> None:
      user = CommandUser().run()
      data = {key: default_json_fields, "USER": user}
      self.appstore.output_config("config", data)
      self.appstore.output_db("db", "")
      self.appstore.output_db("fetch", "")


