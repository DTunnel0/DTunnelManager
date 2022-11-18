from app.terminal.console.common import Port

from app.terminal.console.socks.utils.util import Flag, FlagList, SocksManager
from console.colors import color_name


class SocksStartCallback:
    def __init__(self, socks_manager: SocksManager, port: Port) -> None:
        self.socks_manager = socks_manager
        self.port = port

    def __call__(self, callback) -> None:
        self.socks_manager.port = self.port.value
        self.socks_manager.start()
        callback()


class SocksStopCallback:
    def __init__(self, socks_manager: SocksManager) -> None:
        self.socks_manager = socks_manager

    def __call__(self, callback) -> None:
        self.socks_manager.stop()
        callback()


class CallbackChangePortFlag:
    def __init__(
        self,
        socks_manager: SocksManager,
        flag_list: FlagList,
        flag: Flag,
        port: Port,
    ) -> None:
        self.socks_manager = socks_manager
        self.flag_list = flag_list
        self.flag = flag
        self.port = port

    def execute(self) -> None:
        self.flag.port = self.port.value
        self.flag_list.set(self.flag)
        self.socks_manager.restart()

    def __call__(self) -> None:
        print(color_name.GREEN + 'Porta atual: {}'.format(self.flag.port) + color_name.END)
        self.execute()
