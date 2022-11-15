from app.terminal.console.socks.utils.util import FlagList
from console.colors import color_name
from console.formatter import Formatter, create_line


class FormatterSocks(Formatter):
    def __init__(self, port: int, mode: str, flag_list: FlagList) -> None:
        super().__init__()
        self.port = port
        self.mode = mode
        self.flag_list = flag_list

    def build_menu(self, title):
        menu = super().build_menu(title)

        if self.port <= 0:
            return menu

        values = []
        for flag in self.flag_list._flag_map.values():
            name, port = flag.flag.split()
            name = name.replace('--', '')
            name = name.split('-')[0]
            values.append(name + ' ' + str(port))

        for value in values:
            menu += '%s <-> %s <-> %s\n' % (
                color_name.GREEN + self.mode.ljust(10) + color_name.END,
                color_name.GREEN + str(self.port).rjust(10).ljust(15) + color_name.END,
                color_name.GREEN + str(value).rjust(15) + color_name.END,
            )

        return menu + create_line(color=color_name.BLUE, show=False) + '\n'
