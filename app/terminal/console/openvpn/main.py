import typing as t

from app.terminal.console.openvpn.ovpn_utils.utils import OpenVPNService, OpenVPNUtils

from ..common import Callback, Port, PortValidatorUsed
from console import Console, FuncItem
from app.utilities.logger import logger
from .ovpn_utils import OpenVPNManager


class InstallOpenVPN(Callback):
    def __init__(self, manager: OpenVPNManager, callback: t.Callable) -> None:
        self.manager = manager
        self.callback = callback

    def execute(self) -> None:
        if self.manager.install():
            logger.info('OpenVPN instalado com sucesso!')
        else:
            logger.error('Falha ao instalar OpenVPN!')

        Console.pause()
        self.callback()


class UninstallOpenVPN(Callback):
    def __init__(self, manager: OpenVPNManager, callback: t.Callable) -> None:
        self.manager = manager
        self.callback = callback

    def execute(self) -> None:
        if self.manager.uninstall():
            logger.info('OpenVPN desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar OpenVPN!')

        Console.pause()
        self.callback()


class StartOpenVPN(Callback):
    def __init__(self, manager: OpenVPNManager, callback: t.Callable) -> None:
        self.manager = manager
        self.callback = callback

    def execute(self) -> None:
        if self.manager.start():
            logger.info('OpenVPN iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar OpenVPN!')

        Console.pause()
        self.callback()


class StopOpenVPN(Callback):
    def __init__(self, manager: OpenVPNManager, callback: t.Callable) -> None:
        self.manager = manager
        self.callback = callback

    def execute(self) -> None:
        if self.manager.stop():
            logger.info('OpenVPN parado com sucesso!')
        else:
            logger.error('Falha ao parar OpenVPN!')

        Console.pause()
        self.callback()


class RestartOpenVPN(Callback):
    def __init__(self, manager: OpenVPNManager) -> None:
        self.manager = manager

    def execute(self) -> None:
        if self.manager.restart():
            logger.info('OpenVPN reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar OpenVPN!')

        Console.pause()


class ChangeOpenVPNPort(Callback):
    def __init__(self, manager: OpenVPNManager, port: Port) -> None:
        self.manager = manager
        self.port = port

    def execute(self) -> None:
        try:
            self.manager.change_openvpn_port(self.port.value)
            logger.info('Porta alterada com sucesso!')
            Console.pause()
        except KeyboardInterrupt:
            return


class CreateOVPNFile(Callback):
    def __init__(self, manager: OpenVPNManager) -> None:
        self.manager = manager

    def execute(self) -> None:
        self.manager.create_ovpn_client()
        logger.info('Arquivo OVPN criado com sucesso!')
        Console.pause()


class DeleteOVPNFile(Callback):
    def __init__(self, manager: OpenVPNManager) -> None:
        self.manager = manager

    def execute(self) -> None:
        self.manager.remove_ovpn_client()
        logger.info('Arquivo OVPN deletado com sucesso!')
        Console.pause()


class MainOpenVPNConsole:
    def __init__(self) -> None:
        self.console = Console('OPENVPN Console')
        self.utils = OpenVPNUtils()
        self.service = OpenVPNService(self.utils)
        self.manager = OpenVPNManager(self.utils, self.service)

    def run(self) -> None:
        if not self.utils.is_installed:
            self.console.append_item(
                FuncItem(
                    'INSTALAR OPENVPN',
                    func=InstallOpenVPN(self.manager, self.start),
                    shuld_exit=True,
                )
            )
            self.console.show()
            return

        self.console.append_item(
            FuncItem(
                'PARAR OPENVPN',
                func=StopOpenVPN(self.manager, self.start),
                shuld_exit=True,
            )
            if self.utils.is_running
            else FuncItem(
                'INICIAR OPENVPN',
                func=StartOpenVPN(self.manager, self.start),
                shuld_exit=True,
            )
        )

        self.console.append_item(
            FuncItem(
                'REINICIAR OPENVPN',
                func=RestartOpenVPN(self.manager),
            )
        )

        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA',
                func=ChangeOpenVPNPort(self.manager, Port(PortValidatorUsed())),
            )
        )

        if self.utils.check_exists_ovpn('dtunnel'):
            self.console.append_item(
                FuncItem(
                    'REMOVER ARQUIVO OVPN',
                    func=DeleteOVPNFile(self.manager),
                )
            )
        else:
            self.console.append_item(
                FuncItem(
                    'CRIAR ARQUIVO OVPN',
                    func=CreateOVPNFile(self.manager),
                )
            )

        self.console.append_item(
            FuncItem(
                'DESINSTALAR OPENVPN',
                func=UninstallOpenVPN(self.manager, self.start),
                shuld_exit=True,
            )
        )
        self.console.show()

    def start(self) -> None:
        self.console.items.clear()
        self.console._exit = False
        self.console.selected_exit = False
        self.run()
