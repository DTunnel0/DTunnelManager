import typing as t

from app.infra.controllers.update_user import UpdateUserController
from app.terminal.console.utils import Callback, UserConsole, UserMenuConsole
from app.terminal.console.v2ray.utils.manager import V2RayManager
from app.utilities.logger import logger
from app.utilities.utils import get_ip_address
from console.colors import color_name
from console.console import Console
from console.formatter import create_line


class V2Callback(Callback):
    def __init__(
        self,
        v2ray_manager: V2RayManager,
        pause_screen: bool = True,
        clear_screen: bool = True,
    ):
        self.v2ray_manager = v2ray_manager
        self.pause_screen = pause_screen
        self.clear_screen = clear_screen

    def pause(self) -> None:
        Console.pause()

    def clear(self) -> None:
        Console.clear_screen()


class V2RayInstallCallback(V2Callback):
    def execute(self, action: t.Callable) -> None:
        logger.info('Instalando V2Ray...')
        status = self.v2ray_manager.install()

        if status:
            logger.info('Gere um novo UUID para o cliente.')
            logger.info('V2Ray instalado com sucesso!')
        else:
            logger.error('Falha ao instalar V2Ray!')

        action()


class V2RayUninstallCallback(V2Callback):
    def execute(self, action: t.Callable) -> None:
        logger.info('Desinstalando V2Ray...')
        status = self.v2ray_manager.uninstall()

        if status:
            logger.info('V2Ray desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar V2Ray!')

        action()


class V2RayStartCallback(V2Callback):
    def execute(self, action: t.Callable) -> None:
        logger.info('Iniciando V2Ray...')
        status = self.v2ray_manager.start()

        if status:
            logger.info('V2Ray iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar V2Ray!')

        action()


class V2RayStopCallback(V2Callback):
    def execute(self, action: t.Callable) -> None:
        logger.info('Parando V2Ray...')
        status = self.v2ray_manager.stop()

        if status:
            logger.info('V2Ray parado com sucesso!')
        else:
            logger.error('Falha ao parar V2Ray!')

        action()


class V2RayRestartCallback(V2Callback):
    def execute(self, action: t.Callable) -> None:
        logger.info('Reiniciando V2Ray...')
        status = self.v2ray_manager.restart()

        if status:
            logger.info('V2Ray reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar V2Ray!')

        action()


class V2RayChangePortCallback(V2Callback):
    def execute(self) -> None:
        v2ray_manager = self.v2ray_manager

        current_port = v2ray_manager.get_running_port()
        logger.info('Porta atual: %s' % current_port)

        try:
            port = None
            while port is None:
                try:
                    port = int(input(color_name.YELLOW + 'Porta: ' + color_name.RESET))
                    if port < 1 or port > 65535:
                        raise ValueError

                    if port == v2ray_manager.get_running_port():
                        logger.error('Porta já em uso!')
                        port = None

                except ValueError:
                    logger.error('Porta inválida!')
                    port = None

            if v2ray_manager.change_port(port):
                logger.info('Porta alterada para %s' % port)
            else:
                logger.error('Falha ao alterar porta!')

        except KeyboardInterrupt:
            self.pause_screen = False
            return


class AssociateUserCallback(Callback):
    def __init__(self, update_user_controller: UpdateUserController, uuid: str) -> None:
        self.update_user_controller = update_user_controller
        self.uuid = uuid

    def set_uuid(self, uuid: str) -> None:
        self.uuid = uuid

    def execute(self, user: UserConsole) -> None:
        self.update_user_controller.handle(
            {
                'id': user.id,
                'v2ray_uuid': self.uuid,
            }
        )
        user.v2ray_uuid = self.uuid
        logger.info('Usuário associado com sucesso!')
        Console.pause()
        raise KeyboardInterrupt


class V2RayCreateUUIDCallback(V2Callback):
    def execute(self) -> None:
        self.pause_screen = False
        v2ray_manager = self.v2ray_manager
        uuid = v2ray_manager.create_new_uuid()
        logger.info('UUID criado: %s' % uuid)


class V2RayRemoveUUIDCallback(V2Callback):
    def __init__(
        self,
        uuids: t.List[str],
        users: t.List[UserConsole],
        conetroller: UpdateUserController,
        v2ray_manager: V2RayManager,
        pause_screen: bool = True,
        clear_screen: bool = True,
    ):
        super().__init__(v2ray_manager, pause_screen, clear_screen)
        self.uuids = uuids
        self.users = users
        self.conetroller = conetroller

    def __find_user_by_uuid(self, uuid: str) -> t.Optional[UserConsole]:
        for user in self.users:
            if user.v2ray_uuid == uuid:
                return user

        return None

    def __remove_uuid(self, uuid: str) -> None:
        user = self.__find_user_by_uuid(uuid)
        if user is not None:
            self.conetroller.handle(
                {
                    'id': user.id,
                    'v2ray_uuid': '',
                }
            )
            user.v2ray_uuid = None
        self.uuids.remove(uuid)
        self.v2ray_manager.remove_uuid(uuid)

    def execute(self, uuid: str) -> None:
        self.__remove_uuid(uuid)
        logger.info('UUID removido com sucesso!')
        Console.pause()


class V2RayConfigCallback(V2Callback):
    def execute(self) -> None:
        vless_base_link = 'vless://@{}:{}?encryption={}&type={}#{}'

        ip_address = get_ip_address()
        port = self.v2ray_manager.get_running_port()

        config = self.v2ray_manager.config.load()
        type = config['inbounds'][0]['streamSettings']['network']
        encryption = config['inbounds'][0]['streamSettings'].get('security')
        protocol = config['inbounds'][0]['protocol']

        vless_link = vless_base_link.format(
            ip_address,
            port,
            encryption,
            type,
            '%s:%d' % (ip_address, port),
        )

        Console.clear_screen()
        print(create_line(show=False))
        print(color_name.YELLOW + 'V2Ray Config' + color_name.RESET)
        print(color_name.GREEN + 'IP: %s' % ip_address + color_name.RESET)
        print(color_name.GREEN + 'Port: %s' % port + color_name.RESET)
        print(color_name.GREEN + 'Protocol: %s' % protocol + color_name.RESET)
        print(color_name.GREEN + 'Type: %s' % type + color_name.RESET)
        print(create_line(show=False))

        print(color_name.YELLOW + 'V2Ray Link' + color_name.RESET)
        print(color_name.GREEN + 'Link: %s' % vless_link + color_name.RESET)
        print(create_line(show=False))


class V2RayUUIDListCallback(V2Callback):
    def __init__(
        self,
        console: UserMenuConsole,
        controller: UpdateUserController,
        v2ray_manager: V2RayManager,
        pause_screen: bool = True,
        clear_screen: bool = True,
    ):
        super().__init__(v2ray_manager, pause_screen, clear_screen)
        self.console = console
        self.controller = controller

    def __input(self) -> str:
        text = color_name.YELLOW + 'Deseja associar um usuário? (s/n): ' + color_name.RESET
        return input(text).lower()

    def __should_associate(self) -> bool:
        while True:
            choice = self.__input()
            if choice == 'n':
                return False

            if choice == 's':
                return True

            logger.error('Opção inválida!')

    def execute(self, uuid: str, user: t.Union[UserConsole, None] = None) -> None:
        if user is not None:
            return

        print(color_name.GREEN + 'UUID: %s' % uuid + color_name.RESET)
        if not self.__should_associate():
            return

        self.console.set_callback(AssociateUserCallback(self.controller, uuid))
        self.console.start()
