# from ghrepo.command import Command
from yklibpy.command.command import Command
from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore


class CommandSetup(Command):
  def __init__(self, appstore: AppStore) -> None:
    self.appstore: AppStore = appstore

  def run(self, key: str, default_json_fields: list[str]) -> None:
    user: str | None = CommandGhUser().run()
    if Util.is_empty(user):
      user = CommandGhUser.DEFAULT_VALUE_USER

    data = {key: default_json_fields, "USER": self.appstore.user}
    self.appstore.output_config("config", data)
    self.appstore.output_db("db", {})
    self.appstore.output_db("fetch", {})
