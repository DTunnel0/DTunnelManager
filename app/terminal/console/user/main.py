import datetime
import typing as t
from app.infra.controllers.count_connection import CountUserConnectionController

from app.infra.controllers.create_user import CreateUserController
from app.infra.controllers.delete_user import DeleteUserController
from app.infra.controllers.get_all_users import GetAllUsersController
from app.infra.controllers.get_user import GetUserByUsernameController
from app.infra.controllers.update_user import UpdateUserController
from app.terminal.console.user.console import (
    UserConsole,
    UserMenuConsoleConnectionLimit,
    UserMenuConsoleDeleteUser,
    UserMenuConsoleExpirationDate,
    UserMenuConsolePassword,
)
from app.terminal.console.user.input import ConnectionLimit, ExpirationDate, Password, UserInputData
from console.colors import color_name
from console.console import Console, FuncItem
from console.formatter import create_menu_bg


class Callback:
    def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> None:
        Console.clear_screen()
        try:
            self.execute(*args, **kwargs)
            Console.pause()
        except Exception as e:
            print(color_name.RED + str(e) + color_name.RESET)
            Console.pause()


class CreateUserCallback(Callback):
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
        print(create_menu_bg('CRIAR USUARIO', set_pars=False))
        output = self._create_user_controller.handle(self._data.to_dict())
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


class DeleteUserCallback(Callback):
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


class PasswordChangeCallback(Callback):
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


class ConnectionLimitChangeCallback(Callback):
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


class ExpirationDateChangeCallback(Callback):
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
                'username': input.value,
                'expiration_date': user.expiration_date,
            }
        )
        user.expiration_date = input.value
        print(color_name.GREEN + 'Data de expiracao alterado com sucesso.' + color_name.RESET)


class MonitorCallback(Callback):
    def __init__(
        self,
        count_user_connection_controller: CountUserConnectionController,
        users: t.List[UserConsole],
    ) -> None:
        self._users = users
        self._count_user_connection_controller = count_user_connection_controller

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
            '%02d' % self._count_user_connection_controller.handle(user.username),
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


class MainUserConsole:
    def __init__(
        self,
        create_user_controller: CreateUserController,
        get_all_users_controller: GetAllUsersController,
        delete_user_controller: DeleteUserController,
        update_user_controller: UpdateUserController,
        get_user_by_username_controller: GetUserByUsernameController,
        count_user_connection_controller: CountUserConnectionController,
    ):
        self._create_user_controller = create_user_controller
        self._get_all_users_controller = get_all_users_controller
        self._delete_user_controller = delete_user_controller
        self._update_user_controller = update_user_controller
        self._get_user_by_username_controller = get_user_by_username_controller
        self._count_user_connection_controller = count_user_connection_controller

        self._users: t.List[UserConsole] = []

        self.console = Console('GERENCIADOR DE USUÁRIOS')

    @property
    def users(self) -> t.List[UserConsole]:
        if not self._users:
            self._users = [
                UserConsole.create(user.to_dict())
                for user in self._get_all_users_controller.handle()
            ]
        return self._users

    def run(self) -> None:
        self.console.append_item(
            FuncItem(
                'CRIAR USUÁRIO',
                CreateUserCallback(
                    self._create_user_controller,
                    self._get_user_by_username_controller,
                    self.users,
                    UserInputData(),
                ),
            ),
        )
        self.console.append_item(
            FuncItem(
                'GERAR USUÁRIO',
                CreateUserCallback(
                    self._create_user_controller,
                    self._get_user_by_username_controller,
                    self.users,
                    UserInputData.random(),
                ),
            ),
        )
        self.console.append_item(
            FuncItem(
                'EXCLUIR USUÁRIO',
                UserMenuConsoleDeleteUser(
                    users=self.users,
                    on_select=DeleteUserCallback(
                        self._delete_user_controller,
                        self.users,
                    ),
                ).start,
            ),
        )

        self.console.append_item(
            FuncItem(
                'ALTERAR SENHA',
                UserMenuConsolePassword(
                    users=self.users,
                    on_select=PasswordChangeCallback(
                        self._update_user_controller,
                        self.users,
                    ),
                ).start,
            ),
        )

        self.console.append_item(
            FuncItem(
                'ALTERAR LIMITE DE CONEXÕES',
                UserMenuConsoleConnectionLimit(
                    users=self.users,
                    on_select=ConnectionLimitChangeCallback(
                        self._update_user_controller,
                        self.users,
                    ),
                ).start,
            )
        )

        self.console.append_item(
            FuncItem(
                'ALTERAR DATA DE EXPIRAÇÃO',
                UserMenuConsoleExpirationDate(
                    users=self.users,
                    on_select=ExpirationDateChangeCallback(
                        self._update_user_controller,
                        self.users,
                    ),
                ).start,
            )
        )

        self.console.append_item(
            FuncItem(
                'MONITORAMENTO',
                MonitorCallback(
                    self._count_user_connection_controller,
                    self.users,
                ),
            )
        )
        self.console.show()

    def start(self) -> None:
        self.console._exit = False
        self.console.selected_exit = False
        self.console.items.clear()
        self.run()
