import typing as t

from console import Console, FuncItem
from app.utilities.logger import logger
from .ovpn_utils import OpenVPNManager


class OpenVPNActions:
    openvpn_manager = OpenVPNManager()

    @staticmethod
    def install(callback: t.Callable) -> None:
        status = OpenVPNActions.openvpn_manager.openvpn_install()

        if status:
            logger.info('OpenVPN instalado com sucesso!')
        else:
            logger.error('Falha ao instalar OpenVPN!')

        Console.pause()
        callback()

    @staticmethod
    def uninstall(callback: t.Callable) -> None:
        logger.info('Desinstalando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_uninstall()

        if status:
            logger.info('OpenVPN desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar OpenVPN!')

        Console.pause()
        callback()

    @staticmethod
    def start(callback: t.Callable) -> None:
        logger.info('Iniciando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_start()

        if status:
            logger.info('OpenVPN iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar OpenVPN!')

        Console.pause()
        callback()

    @staticmethod
    def stop(callback: t.Callable) -> None:
        logger.info('Parando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_stop()

        if status:
            logger.info('OpenVPN parado com sucesso!')
        else:
            logger.error('Falha ao parar OpenVPN!')

        Console.pause()
        callback()

    @staticmethod
    def restart(callback: t.Callable) -> None:
        logger.info('Reiniciando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_restart()

        if status:
            logger.info('OpenVPN reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar OpenVPN!')

        Console.pause()
        callback()

    @staticmethod
    def change_port():
        current_port = OpenVPNActions.openvpn_manager.get_current_port()
        logger.info('Porta atual: {}'.format(current_port))

        port = None
        while not port:
            port = input('Porta: ')

            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError
            except ValueError:
                logger.error('Porta inválida!')
                port = None

        OpenVPNActions.openvpn_manager.change_openvpn_port(port)
        OpenVPNActions.openvpn_manager.openvpn_restart()
        logger.info('Porta alterada para {}!'.format(port))
        Console.pause()


class MainOpenVPNConsole:
    def __init__(self) -> None:
        self.console = Console('OPENVPN Console')

    def run(self) -> None:
        if not OpenVPNManager.ovpn_utils.openvpn_is_installed():
            self.console.append_item(
                FuncItem(
                    'INSTALAR OPENVPN',
                    func=lambda: OpenVPNActions.install(self.start),
                    shuld_exit=True,
                )
            )
            self.console.show()
            return

        if OpenVPNManager.ovpn_utils.openvpn_is_running():
            self.console.append_item(
                FuncItem(
                    'PARAR OPENVPN',
                    func=lambda: OpenVPNActions.stop(self.start),
                )
            )
        else:
            self.console.append_item(
                FuncItem(
                    'INICIAR OPENVPN',
                    func=lambda: OpenVPNActions.start(self.start),
                    shuld_exit=True,
                )
            )
        self.console.append_item(
            FuncItem(
                'REINICIAR OPENVPN',
                func=lambda: OpenVPNActions.restart(self.start),
                shuld_exit=True,
            )
        )
        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA',
                func=lambda: OpenVPNActions.change_port(),
            )
        )

        self.console.append_item(
            FuncItem(
                'DESINSTALAR OPENVPN',
                func=lambda: OpenVPNActions.uninstall(self.start),
                shuld_exit=True,
            )
        )
        self.console.show()

    def start(self) -> None:
        self.console.items.clear()
        self.console._exit = False
        self.console.selected_exit = False
        self.run()
