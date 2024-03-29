import typing as t

from app.domain.use_cases.user.update_user import UpdateUserUseCase, UserUpdateInputDTO

from ..common import Callback
from ..user.console import UserConsole, UserMenuConsole
from .utils.manager import V2RayManager

from ....utilities.logger import logger
from ....utilities.utils import get_ip_address

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
    def execute(self, *args, **kwargs) -> None:
        action: t.Callable = args[0]
        logger.info('Instalando V2Ray...')
        status = self.v2ray_manager.install()

        if status:
            logger.info('Gere um novo UUID para o cliente.')
            logger.info('V2Ray instalado com sucesso!')
        else:
            logger.error('Falha ao instalar V2Ray!')

        action()


class V2RayUninstallCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
        action: t.Callable = args[0]

        logger.info('Desinstalando V2Ray...')
        status = self.v2ray_manager.uninstall()

        if status:
            logger.info('V2Ray desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar V2Ray!')

        action()


class V2RayStartCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
        action: t.Callable = args[0]
        logger.info('Iniciando V2Ray...')
        status = self.v2ray_manager.start()

        if status:
            logger.info('V2Ray iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar V2Ray!')

        action()


class V2RayStopCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
        action: t.Callable = args[0]
        logger.info('Parando V2Ray...')
        status = self.v2ray_manager.stop()

        if status:
            logger.info('V2Ray parado com sucesso!')
        else:
            logger.error('Falha ao parar V2Ray!')

        action()


class V2RayRestartCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
        action: t.Callable = args[0]
        logger.info('Reiniciando V2Ray...')
        status = self.v2ray_manager.restart()

        if status:
            logger.info('V2Ray reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar V2Ray!')

        action()


class V2RayChangePortCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
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


class AssociateUserCallback(V2Callback):
    def __init__(self, update_user: UpdateUserUseCase, uuid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_user = update_user
        self.uuid = uuid

    def set_uuid(self, uuid: str) -> None:
        self.uuid = uuid

    def execute(self, *args, **kwargs) -> None:
        user: UserConsole = args[0]
        self.update_user.execute(
            UserUpdateInputDTO(
                id=user.id,
                v2ray_uuid=self.uuid,
            )
        )
        user.v2ray_uuid = self.uuid
        self.v2ray_manager.edit_client(self.uuid, user.username)
        logger.info('Usuário associado com sucesso!')
        Console.pause()
        raise KeyboardInterrupt


class V2RayCreateUUIDCallback(V2Callback):
    def __init__(self, uuids: t.List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uuids = uuids

    def execute(self, *args, **kwargs) -> None:
        self.pause_screen = False
        v2ray_manager = self.v2ray_manager
        uuid = v2ray_manager.create_client()
        logger.info('UUID criado: %s' % uuid)
        self.uuids.append(uuid)
        self.pause()


class V2RayRemoveUUIDCallback(V2Callback):
    def __init__(
        self,
        uuids: t.List[str],
        users: t.List[UserConsole],
        update_user: UpdateUserUseCase,
        v2ray_manager: V2RayManager,
        pause_screen: bool = True,
        clear_screen: bool = True,
    ):
        super().__init__(v2ray_manager, pause_screen, clear_screen)
        self.uuids = uuids
        self.users = users
        self.update_user = update_user

    def __remove_uuid(self, uuid: str, user: UserConsole) -> None:
        if user is not None:
            self.update_user.execute(
                UserUpdateInputDTO(
                    id=user.id,
                    v2ray_uuid='',
                )
            )
            user.v2ray_uuid = None
        self.uuids.remove(uuid)
        self.v2ray_manager.delete_client(uuid)

    def execute(self, *args, **kwargs) -> None:
        uuid: str = args[0]
        user: UserConsole = args[1]

        self.__remove_uuid(uuid, user)
        logger.info('UUID removido com sucesso!')
        self.pause()


class V2RayConfigCallback(V2Callback):
    def execute(self, *args, **kwargs) -> None:
        vless_base_link = 'vless://@{}:{}?encryption={}&type={}#{}'

        ip_address = get_ip_address()
        port = self.v2ray_manager.get_running_port()

        config = self.v2ray_manager.config.load()
        type = config['inbounds'][-1]['streamSettings']['network']
        encryption = config['inbounds'][-1]['streamSettings'].get('security')
        protocol = config['inbounds'][-1]['protocol']

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
        self.pause()


class V2RayUUIDListCallback(V2Callback):
    def __init__(
        self,
        console: UserMenuConsole,
        update_user: UpdateUserUseCase,
        v2ray_manager: V2RayManager,
        pause_screen: bool = True,
        clear_screen: bool = True,
    ):
        super().__init__(v2ray_manager, pause_screen, clear_screen)
        self.console = console
        self.update_user = update_user

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

    def execute(self, *args, **kwargs) -> None:
        uuid: str = args[0]
        user: t.Union[UserConsole, None] = args[1]
        if user is not None:
            return

        print(color_name.GREEN + 'UUID: %s' % uuid + color_name.RESET)
        if not self.__should_associate():
            return

        self.console.set_callback(AssociateUserCallback(self.update_user, uuid, self.v2ray_manager))
        self.console.start()
