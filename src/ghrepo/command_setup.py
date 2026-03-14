# from ghrepo.command import Command
from yklibpy.command.command import Command
from yklibpy.command.command_gh_user import CommandGhUser
from yklibpy.common.util import Util
from yklibpy.db.appstore import AppStore


class CommandSetup(Command):
    """設定ファイルと空の保存領域を初期化するコマンドを表す。"""

    def __init__(self, appstore: AppStore) -> None:
        """初期化先の `AppStore` を保持する。"""
        self.appstore: AppStore = appstore

    def run(self, key: str, default_json_fields: list[str]) -> None:
        """設定値と空の DB を出力して初回利用状態を整える。

        GitHub ユーザーが取得できない場合は既定値へフォールバックする。
        """
        user: str | None = CommandGhUser().run()
        if Util.is_empty(user):
            user = CommandGhUser.DEFAULT_VALUE_USER

        data = {key: default_json_fields, "USER": self.appstore.user}
        self.appstore.output_config("config", data)
        self.appstore.output_db("db", {})
        self.appstore.output_db("fetch", {})
