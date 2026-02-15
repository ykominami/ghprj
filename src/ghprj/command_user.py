from ghprj.command import Command


class CommandUser(Command):
    def __init__(self):
        pass

    def run(self) -> str:
        command_line = f'gh api user --jq ".login"'
        str = self.run_command_simple(command_line)
        # print(str)
        return str
