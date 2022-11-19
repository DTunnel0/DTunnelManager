import typing as t

from app.infra.controllers.user.count_connection import CountUserConnectionController
from app.infra.controllers.user.create import CreateUserController
from app.infra.controllers.user.delete import DeleteUserController
from app.infra.controllers.user.get_all import GetAllUsersController
from app.infra.controllers.user.get_user import GetUserByUsernameController
from app.infra.controllers.user.update import UpdateUserController
from app.terminal.console.user.callback import (
    ConnectionLimitChangeCallback,
    CreateUserCallback,
    DeleteUserCallback,
    ExpirationDateChangeCallback,
    MonitorCallback,
    PasswordChangeCallback,
)
from app.terminal.console.user.console import (
    UserConsole,
    UserMenuConsoleConnectionLimit,
    UserMenuConsoleDeleteUser,
    UserMenuConsoleExpirationDate,
    UserMenuConsolePassword,
)
from app.terminal.console.user.input import RandomUserInputData, UserInputData
from console.console import Console, FuncItem


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
            self._users.extend(
                [
                    UserConsole.create(user.to_dict())
                    for user in self._get_all_users_controller.handle()
                ]
            )
        return self._users

    def run(self) -> None:
        self.console.append_item(
            FuncItem(
                'CRIAR USUÁRIO',
                lambda: CreateUserCallback(
                    self._create_user_controller,
                    self._get_user_by_username_controller,
                    self.users,
                    UserInputData(),
                )(),
            ),
        )
        self.console.append_item(
            FuncItem(
                'GERAR USUÁRIO',
                lambda: CreateUserCallback(
                    self._create_user_controller,
                    self._get_user_by_username_controller,
                    self.users,
                    RandomUserInputData(),
                )(),
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
