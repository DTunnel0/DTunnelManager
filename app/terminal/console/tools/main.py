import json
import os
import re
import typing as t
import datetime

from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO

from app.utilities.logger import logger
from app.version import __version__

from console import Console, FuncItem
from console.colors import color_name


class DTUpdate:
    def __init__(self):
        self.repository_url = 'https://github.com/DTunnel0/DTunnelManager.git'
        self.version_url = (
            'https://raw.githubusercontent.com/DTunnel0/DTunnelManager/master/app/version.py'
        )

    def check_update(self) -> bool:
        data = os.popen('curl -sL ' + self.version_url).read().strip()
        pattern = re.compile(r'__version__ = \'(.*)\'')
        match = pattern.search(data)

        if not match:
            return False

        version = match.group(1)
        if version == __version__:
            logger.warn('Nao foi encontrado atualizacoes')
            return False

        logger.success('Foi encontrada uma atualizacao')  # type: ignore
        logger.success('Versao atual: ' + __version__)  # type: ignore
        logger.success('Versao nova: ' + version)  # type: ignore

        return True

    def update(self) -> None:
        os.chdir(os.path.expanduser('~'))

        if os.path.exists('DTunnelManager'):
            os.system('rm -rf DTunnelManager')

        os.system('echo \'y\' | pip3 uninstall DTunnelManager')

        os.system('git clone ' + self.repository_url)
        os.chdir('DTunnelManager')
        os.system('pip3 install -r requirements.txt')
        os.system('python3 setup.py install')

        logger.success('Atualizacao realizada com sucesso')  # type: ignore
        logger.success('Execute: `vps` para entrar no menu')  # type: ignore
        exit(0)


def check_update() -> None:
    dt_update = DTUpdate()
    if dt_update.check_update():

        result = input(color_name.YELLOW + 'Deseja atualizar? (S/N) ' + color_name.RESET)

        if result.upper() == 'S':
            dt_update.update()

    Console.pause()


class Backup:
    def __init__(self, name: str, path: str) -> None:
        self._name = name
        self._path = path

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def full_path(self) -> str:
        return os.path.join(self._path, self._name)


class RestoreBackup:
    def __init__(self, backup: Backup, create_user: CreateUserUseCase) -> None:
        self._backup = backup
        self.create_user = create_user

    @property
    def backup(self) -> Backup:
        return self._backup

    def restore(self) -> None:
        raise NotImplementedError


class CreateBackup:
    def __init__(self, backup: Backup) -> None:
        self._backup = backup

    @property
    def backup(self) -> Backup:
        return self._backup

    def create(self) -> None:
        raise NotImplementedError


class SSHPlusBackup(Backup):
    def __init__(self):
        super().__init__('backup.vps', '/root/')


class DTBackup(Backup):
    def __init__(self):
        super().__init__('dtbackup.tar.gz', '/root/')


class SSHPlusRestoreBackup(RestoreBackup):
    def check_exists_user(self, username: str) -> bool:
        command = 'id {} >/dev/null 2>&1'
        result = os.system(command.format(username))
        return result == 0

    def get_limit_user(self, username: str) -> int:
        path = '/root/usuarios.db'

        try:
            with open(path, 'r') as file:
                for line in file:
                    if line.startswith(username):
                        return int(line.split()[1])
        except Exception as e:
            logger.error(e)

        return 1

    def get_expiration_date(self, username: str) -> str:
        command = 'chage -l {} | grep "Account expires"'
        data = os.popen(command.format(username)).read()
        expiration_date = data.strip().split(':')[-1].strip()  # FOMRAT: Apr 06, 2023 | never
        return expiration_date

    def format_expiration_date(
        self,
        expiration_date: str,
        default: datetime.datetime,
    ) -> datetime.datetime:
        if expiration_date == 'never':
            return default

        date = datetime.datetime.strptime(expiration_date, '%b %d, %Y')
        return date

    def get_v2ray_uuid(self, username: str) -> t.Optional[str]:
        path = '/etc/v2ray/config.json'

        try:
            with open(path, 'r') as file:
                data = json.load(file)
                for list_data in data['inbounds']:
                    if 'settings' in list_data and 'clients' in list_data['settings']:
                        for client in list_data['settings']['clients']:
                            if client['email'] == username:
                                return client['id']
        except Exception as e:
            logger.error(e)

        return None

    def restore_users(self) -> None:
        path = '/etc/SSHPlus/senha/'
        for username in os.listdir(path):
            if not self.check_exists_user(username):
                return

            password = open(os.path.join(path, username), 'r').read().strip()
            limit = self.get_limit_user(username)
            expiration_date = self.get_expiration_date(username)
            v2ray_uuid = self.get_v2ray_uuid(username)

            try:
                self.create_user.execute(
                    UserInputDTO(
                        username=username,
                        password=password,
                        connection_limit=limit,
                        expiration_date=self.format_expiration_date(
                            expiration_date,
                            datetime.datetime.now(),
                        ),
                        v2ray_uuid=v2ray_uuid,
                    )
                )
            except Exception as e:
                logger.error(e)

    def restore(self) -> None:
        logger.info('Restaurando SSHPlus...')

        command = 'tar -xvf {} --directory / >/dev/null 2>&1'
        result = os.system(command.format(self.backup.full_path))

        if result != 0:
            logger.error('Falha ao restaurar SSHPlus')
            return

        self.restore_users()
        logger.info('Restaurado com sucesso!')


class GLBackupRestoreBackup(RestoreBackup):
    def restore(self) -> None:
        logger.error('Desculpe, mas eu não fui implementado ainda!')


def restore_backup(backup: RestoreBackup) -> None:
    if not isinstance(backup, RestoreBackup):
        logger.error('O backup precisa ser uma instância de RestoreBackup!')
        Console.pause()
        return

    if not os.path.isfile(backup.backup.full_path):
        logger.error('Não foi encontrado o arquivo \'%s\'!', backup.backup.full_path)
        Console.pause()
        return

    backup.restore()
    Console.pause()


def choice_restore_backup(create_user: CreateUserUseCase) -> None:
    console = Console('RESTAURAR BACKUP')
    console.append_item(
        FuncItem(
            'SSHPLUS',
            lambda: restore_backup(SSHPlusRestoreBackup(SSHPlusBackup(), create_user)),
        )
    )
    console.append_item(
        FuncItem(
            'GLBACKUP',
            lambda: restore_backup(GLBackupRestoreBackup(DTBackup(), create_user)),
        )
    )
    console.show()


class MainToolsConsole:
    def __init__(self, create_user: CreateUserUseCase) -> None:
        self.create_user = create_user
        self.console = Console('GERENCIADOR DE FERRAMENTAS')

    def run(self) -> None:
        self.console.append_item(FuncItem('VERFICAR ATUALIZAÇÕES', check_update))
        self.console.append_item(FuncItem('CRIAR BACKUP', input))
        self.console.append_item(
            FuncItem(
                'RESTAURAR BACKUP',
                choice_restore_backup,
                self.create_user,
            )
        )
        self.console.show()

    def start(self) -> None:
        self.console.items.clear()
        self.console._exit = False
        self.console.selected_exit = False
        self.run()
