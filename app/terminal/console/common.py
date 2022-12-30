import os

from abc import ABCMeta, abstractmethod
from app.utilities.logger import logger
from console.colors import color_name
from console.console import Console

from typing import Generic, TypeVar


class Callback(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> None:
        try:
            self.execute(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            Console.pause()


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
