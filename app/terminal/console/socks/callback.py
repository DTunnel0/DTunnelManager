import typing as t
import os
import re

from app.terminal.console.socks.utils.util import Flag, FlagList, SocksManager
from console.colors import color_name


class PortValidator:
    def validate(self, port: int) -> None:
        if port < 1 or port > 65535:
            raise ValueError('Porta inválida')


class PortValidatorUsed(PortValidator):
    def validate(self, port: int) -> None:
        super().validate(port)
        cmd = 'netstat -tulpn | grep -v grep | grep -w {}'.format(port)
        result = os.popen(cmd).read()
        if result:
            raise ValueError('A porta {port} já está em uso'.format(port=port))


class Port:
    def __init__(self, validator: PortValidator = PortValidator()) -> None:
        self._validator = validator

    @property
    def value(self) -> int:
        return self.__input()

    def __input(self) -> int:
        while True:
            try:
                port = int(input(color_name.GREEN + 'PORTA: ' + color_name.RESET))
                self._validator.validate(port)
                return port
            except ValueError as e:
                print(color_name.RED + str(e) + color_name.RESET)


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
