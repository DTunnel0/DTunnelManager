import datetime
import typing as t

from console.colors import color_name
from console.console import Console
from console.formatter import create_menu_bg

from ....infra.controllers.user.count_connection import CountUserConnectionController
from ....infra.controllers.user.create import CreateUserController
from ....infra.controllers.user.delete import DeleteUserController
from ....infra.controllers.user.get_user import GetUserByUsernameController
from ....infra.controllers.user.update import UpdateUserController
from ..common import Callback
from .console import UserConsole
from .input import ConnectionLimit, ExpirationDate, Password, UserInputData


class UserCallback(Callback):
    def __call__(self, *args, **kwargs) -> None:
        Console.clear_screen()
        super().__call__(*args, **kwargs)
        Console.pause()


class CreateUserCallback(UserCallback):
    def __init__(
        self,
        _create_user_controller: CreateUserController,
        get_user_by_username_controller: GetUserByUsernameController,
        users: t.List[UserConsole],
        input_data: UserInputData,
    ) -> None:
        self._create_user_controller = _create_user_controller
        self._get_user_by_username_controller = get_user_by_username_controller
        self._users = users
        self._data = input_data

    def execute(self) -> None:
        try:
            print(create_menu_bg('CRIAR USUARIO', set_pars=False))
            output = self._create_user_controller.handle(
                {
                    'username': self._data.username,
                    'password': self._data.password,
                    'connection_limit': self._data.connection_limit,
                    'expiration_date': self._data.expiration_date.isoformat(),
                }
            )
            user_console = UserConsole(
                id=self._get_user_by_username_controller.handle(self._data.username)['id'],
                username=self._data.username,
                password=self._data.password,
                connection_limit=self._data.connection_limit,
                expiration_date=self._data.expiration_date,
                v2ray_uuid=self._data.v2ray_uuid,
            )
            self._users.append(user_console)
            Console.clear_screen()
            print(output)
        except KeyboardInterrupt:
            return


class DeleteUserCallback(UserCallback):
    def __init__(
        self,
        delete_user_controller: DeleteUserController,
        users: t.List[UserConsole],
    ) -> None:
        self._delete_user_controller = delete_user_controller
        self._users = users

    def execute(self, user: UserConsole) -> None:
        self._delete_user_controller.handle(user.id)
        self._users.remove(user)
        print(color_name.GREEN + 'Usuario deletado com sucesso.' + color_name.RESET)


class PasswordChangeCallback(UserCallback):
    def __init__(
        self,
        update_user_controller: UpdateUserController,
        users: t.List[UserConsole],
    ) -> None:
        self._update_user_controller = update_user_controller
        self._users = users

    def execute(self, user: UserConsole) -> None:
        print(create_menu_bg('ALTERAR SENHA', set_pars=False))
        print(color_name.GREEN + 'Usuario: ' + color_name.RESET + user.username)
        print(color_name.GREEN + 'Senha atual: ' + color_name.RESET + user.password)

        input = Password()
        self._update_user_controller.handle(
            {
                'id': user.id,
                'username': user.username,
                'password': input.value,
            }
        )
        user.password = input.value
        print(color_name.GREEN + 'Senha alterada com sucesso.' + color_name.RESET)


class ConnectionLimitChangeCallback(UserCallback):
    def __init__(
        self,
        update_user_controller: UpdateUserController,
        users: t.List[UserConsole],
    ) -> None:
        self._update_user_controller = update_user_controller
        self._users = users

    def execute(self, user: UserConsole) -> None:
        print(create_menu_bg('ALTERAR LIMITE DE CONEXOES', set_pars=False))
        print(color_name.GREEN + 'Usuario: ' + color_name.RESET + user.username)
        print(
            color_name.GREEN
            + 'Limite de conexoes atual: '  # noqa: W503
            + color_name.RESET  # noqa: W503
            + '%02d' % user.connection_limit  # noqa: W503
        )

        input = ConnectionLimit()
        self._update_user_controller.handle(
            {
                'id': user.id,
                'connection_limit': input.value,
            }
        )
        user.connection_limit = input.value
        print(color_name.GREEN + 'Limite de conexoes alterado com sucesso.' + color_name.RESET)


class ExpirationDateChangeCallback(UserCallback):
    def __init__(
        self,
        update_user_controller: UpdateUserController,
        users: t.List[UserConsole],
    ) -> None:
        self._update_user_controller = update_user_controller
        self._users = users

    def execute(self, user: UserConsole) -> None:
        print(create_menu_bg('ALTERAR DATA DE EXPIRACAO', set_pars=False))
        print(color_name.GREEN + 'Usuario: ' + color_name.RESET + user.username)
        print(
            color_name.GREEN
            + 'Data de expiracao atual: '  # noqa: W503
            + color_name.RESET  # noqa: W503
            + user.expiration_date.strftime('%d/%m/%Y')  # noqa: W503
        )

        input = ExpirationDate()
        self._update_user_controller.handle(
            {
                'id': user.id,
                'username': user.username,
                'expiration_date': input.value,
            }
        )
        user.expiration_date = input.value
        print(color_name.GREEN + 'Data de expiracao alterado com sucesso.' + color_name.RESET)


class MonitorCallback(Callback):
    def __init__(
        self,
        controller: CountUserConnectionController,
        users: t.List[UserConsole],
    ) -> None:
        self._users = users
        self.controller = controller

    def __build_header(self) -> str:
        items = ['USUARIO', 'CONEXOES', 'LIMITE', 'EXPIRACAO']
        sep = '|'
        size_header = 50
        size_item = int(size_header // len(items)) - len(sep)

        header = color_name.GREEN + '-' * size_header + color_name.RESET + '\n'
        header += color_name.GREEN + sep + color_name.RESET
        for item in items:
            header += (
                color_name.GREEN
                + item.center(size_item)
                + color_name.RESET
                + color_name.GREEN
                + sep
                + color_name.RESET
            )
        header += '\n' + color_name.GREEN + '-' * size_header + color_name.RESET
        return header

    def __build_line(self, user: UserConsole) -> str:
        items = [
            user.username,
            '%02d' % self.controller.handle(user.username),
            '%02d' % user.connection_limit,
            '%02d dias' % (user.expiration_date - datetime.datetime.now()).days,
        ]
        size_header = 50
        size_item = int(size_header / len(items)) - 1
        sep = '|'

        line = color_name.GREEN + sep + color_name.RESET
        for item in items:
            line += (
                color_name.YELLOW
                + item.center(size_item)
                + color_name.GREEN
                + sep
                + color_name.RESET
            )
        return line

    def execute(self) -> None:
        Console.clear_screen()
        if not self._users:
            print(color_name.RED + 'Nenhum usuario cadastrado.' + color_name.RESET)
            return

        while True:
            print(create_menu_bg('MONITORAMENTO', set_pars=False))
            print(self.__build_header())
            for user in self._users:
                print(self.__build_line(user))
            print(color_name.GREEN + '-' * 50 + color_name.RESET + '\n')
            try:
                input(color_name.GREEN + 'Pressione ENTER para atualizar.' + color_name.RESET)
                Console.clear_screen()
            except KeyboardInterrupt:
                break
