import os
import typing as t

from app.utilities.logger import logger
from console import Console, FuncItem
from console.colors import color_name
from console.formatter import Formatter, create_line, create_menu_bg


def check_screen_is_installed():
    command = 'command -v screen >/dev/null 2>&1'
    return os.system(command) == 0


def process_install_screen():
    if check_screen_is_installed():
        return

    answer = input(
        color_name.YELLOW + 'Screen não está instalado. Deseja instalar? [s/N]: ' + color_name.END
    )
    if answer.lower() == 's':
        logger.info('Instalando screen...')
        os.system('sudo apt-get install screen -y >/dev/null 2>&1')
        logger.info('Screen instalado com sucesso!')
        Console.pause()


class BadvpnInstaller:
    _badvpn_url = 'https://github.com/DuTra01/tron_ssh/raw/master/badvpn-udpgw'
    _badvpn_file = 'badvpn-udpgw'
    _badvpn_path = '/usr/bin/badvpn-udpgw'

    @classmethod
    def install(cls) -> bool:
        if os.path.exists(cls._badvpn_path):
            return True

        if os.system('command -v wget >/dev/null 2>&1') != 0:
            logger.error('Por favor, instale o wget')
            return False

        logger.info('Baixando o BadVPN...')
        if os.system('wget %s' % (cls._badvpn_url)) != 0:
            logger.error('Não foi possível baixar o badvpn-udpgw')
            return False

        if os.system('mv %s %s' % (cls._badvpn_file, cls._badvpn_path)) != 0:
            logger.error('Não foi possível mover o badvpn-udpgw para o diretório de execução')
            return False

        if os.system('chmod a+x %s' % (cls._badvpn_path)) != 0:
            logger.error('Não foi possível dar permissão de execução ao badvpn-udpgw')
            return False

        command = '%s --help' % cls._badvpn_path
        if os.system(command) != 0:
            logger.error('Não foi possível executar o badvpn-udpgw')
            return False

        logger.info('BadVPN instalado com sucesso')
        return True

    @classmethod
    def uninstall(cls) -> bool:
        if not os.path.exists(cls._badvpn_path):
            return True

        os.system(f'rm {cls._badvpn_path}')

        return not os.path.exists(cls._badvpn_path)

    @classmethod
    def is_installed(cls) -> bool:
        return os.path.exists(cls._badvpn_path)


class BadvpnFlag:
    def __init__(
        self,
        listen_addr: str = '127.0.0.1:7300',
        max_clients: int = 1100,
    ) -> None:
        self.__listen_addr = listen_addr
        self.__max_clients = max_clients

        self.__badvpn_executable = BadvpnInstaller._badvpn_path

    @property
    def listen_addr(self) -> str:
        return self.__listen_addr

    @property
    def max_clients(self) -> int:
        return self.__max_clients

    @property
    def flag(self) -> str:
        return '--listen-addr {0} --max-clients {1}'.format(
            self.__listen_addr,
            self.__max_clients,
        )

    def command(self) -> str:
        return '{0} {1}'.format(self.__badvpn_executable, self.flag)


class BadvpnScreenManager:
    __screen_name_prefix = 'badvpn'

    def __init__(self, flag: BadvpnFlag) -> None:
        self.__flag = flag
        self.__screen_name = '{0}_{1}'.format(
            self.__screen_name_prefix,
            self.__flag.listen_addr.replace(':', '_'),
        )

        self.__screen_command = 'screen -dmS {0} {1}'.format(
            self.__screen_name,
            self.__flag.command(),
        )

    @staticmethod
    def list_of_screen() -> t.List[str]:
        data = os.popen('bash -c \'screen -ls 2>/dev/null\'').read().strip()
        names = []

        for line in data.split('\n'):
            if BadvpnScreenManager.__screen_name_prefix in line:
                names.append(line.split()[0].strip().split('.', 1)[1])

        return names

    @staticmethod
    def list_of_ports() -> t.List[int]:
        names = BadvpnScreenManager.list_of_screen()
        return [int(name.split('_')[-1]) for name in names]

    def is_running(self, screen_name: str = None) -> bool:
        if screen_name is None:
            screen_name = self.__screen_name

        return screen_name in self.list_of_screen()

    def start(self) -> bool:
        if self.is_running():
            return True

        if os.system(self.__screen_command) != 0:
            logger.error('Não foi possível iniciar o BadVPN')
        else:
            logger.info('BadVPN iniciado com sucesso')

        return self.is_running()

    def stop(self) -> bool:
        if not self.is_running():
            return True

        if os.system('screen -S {0} -X quit'.format(self.__screen_name)) != 0:
            logger.error('Não foi possível parar o BadVPN')
        else:
            logger.info('BadVPN parado com sucesso')

        return not self.is_running()


class FormatterBadvpn(Formatter):
    def __init__(self) -> None:
        super().__init__()

    def build_menu(self, title):
        menu = super().build_menu(title)

        ports = BadvpnScreenManager.list_of_ports()
        if len(ports) <= 0:
            return menu

        menu += color_name.YELLOW + 'Em uso: %s\n' % ', '.join(map(str, ports)) + color_name.END

        return menu + create_line(color=color_name.BLUE, show=False) + '\n'


def action_install_badvpn(callback: t.Callable[[], None]) -> None:
    BadvpnInstaller.install()
    Console.pause()
    callback()


def action_uninstall_badvpn(callback: t.Callable[[], None]) -> None:
    BadvpnInstaller.uninstall()
    Console.pause()
    callback()


def action_open_port():
    try:
        port = int(input(color_name.YELLOW + 'Porta: ' + color_name.END))

        flag = BadvpnFlag(listen_addr='127.0.0.1:%s' % port, max_clients=1100)
        screen = BadvpnScreenManager(flag=flag)
        screen.start()
    except ValueError:
        logger.error('Porta inválida')

    Console.pause()


def action_close_port():
    ports = BadvpnScreenManager.list_of_ports()
    if not ports:
        logger.error('Nenhuma porta ativa')
        Console.pause()
        return

    console = Console('SELECIONE UMA PORTA')
    for port in ports:
        console.append_item(FuncItem(str(port), lambda x: x, port, exit_on_select=True))

    console.show()

    if console.selected_exit:
        return

    port = int(console.item_returned)
    flag = BadvpnFlag(listen_addr='127.0.0.1:%s' % port, max_clients=1100)
    screen = BadvpnScreenManager(flag=flag)
    screen.stop()

    Console.pause()
    action_close_port()


class MainBadVpnConsole:
    def __init__(self) -> None:
        self.console = Console('BadVPN Console', formatter=FormatterBadvpn())

    def run(self) -> None:
        if not BadvpnInstaller.is_installed():
            self.console.append_item(
                FuncItem(
                    'INSTALAR BadVPN',
                    action_install_badvpn,
                    self.start,
                    shuld_exit=True,
                )
            )
            self.console.show()
            return

        self.console.append_item(
            FuncItem(
                'ABRIR PORTA',
                action_open_port,
            )
        )
        self.console.append_item(
            FuncItem(
                'FECHAR PORTA',
                action_close_port,
            )
        )

        self.console.append_item(
            FuncItem(
                'DESINSTALAR BadVPN',
                action_uninstall_badvpn,
                self.start,
                shuld_exit=True,
            )
        )

        self.console.show()

    def start(self) -> None:
        self.console.items.clear()
        self.console._exit = False
        self.console.selected_exit = False
        self.run()
