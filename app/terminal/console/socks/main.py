from app.terminal.console.socks.fomatter import FormatterSocks
from console.console import Console, FuncItem

from .callback import (
    CallbackChangePortFlag,
    Port,
    PortValidatorUsed,
    SocksStartCallback,
    SocksStopCallback,
)
from .utils.util import FlagList, OpenVpnFlag, SocksManager, SSHFlag, V2rayFlag


class MainSocksConsole:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.socks_manager = SocksManager(
            SocksManager.get_running_port(mode),
            FlagList(
                [
                    OpenVpnFlag.create('OPENVPN', 1194),
                    SSHFlag.create('SSH', 22),
                    V2rayFlag.create('V2RAY', 1080),
                ]
            ),
            mode,
        )

        self.formatter = FormatterSocks(
            self.socks_manager.port,
            self.mode,
            self.socks_manager.flag_list,
        )
        self.console = Console(
            'SOCKS Manager ' + mode.upper(),
            formatter=self.formatter,
        )

    def run(self):
        if not self.socks_manager.is_running():
            self.formatter.port = -1
            self.console.append_item(
                FuncItem(
                    'INICIAR',
                    SocksStartCallback(
                        self.socks_manager,
                        Port(
                            PortValidatorUsed(),
                        ),
                    ),
                    self.start,
                    shuld_exit=True,
                )
            )
            self.console.show()
            return

        self.formatter.port = self.socks_manager.port
        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA OPENVPN',
                CallbackChangePortFlag(
                    self.socks_manager,
                    self.socks_manager.flag_list,
                    self.socks_manager.flag_list.get('OPENVPN'),
                    Port(),
                ),
            )
        )
        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA SSH',
                CallbackChangePortFlag(
                    self.socks_manager,
                    self.socks_manager.flag_list,
                    self.socks_manager.flag_list.get('SSH'),
                    Port(),
                ),
            )
        )
        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA V2RAY',
                CallbackChangePortFlag(
                    self.socks_manager,
                    self.socks_manager.flag_list,
                    self.socks_manager.flag_list.get('V2RAY'),
                    Port(),
                ),
            )
        )
        self.console.append_item(
            FuncItem(
                'PARAR',
                SocksStopCallback(self.socks_manager),
                self.start,
                shuld_exit=True,
            )
        )
        self.console.show()

    def start(self):
        self.console._exit = False
        self.console.selected_exit = False
        self.console.items.clear()
        self.run()
