import typing as t


from app.domain.use_cases.user.count_connections import CountUserConnection
from app.domain.use_cases.user.create_user import CreateUserUseCase
from app.domain.use_cases.user.delete_user import DeleteUserUseCase
from app.domain.use_cases.user.get_user import (
    GetAllUsersUseCase,
    GetUserByUsernameUseCase,
    GetUserByUUIDUseCase,
)
from app.domain.use_cases.user.update_user import UpdateUserUseCase

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
        create_user: CreateUserUseCase,
        get_all_users: GetAllUsersUseCase,
        delete_user: DeleteUserUseCase,
        update_user: UpdateUserUseCase,
        get_user_by_username: GetUserByUsernameUseCase,
        count_user_connection: CountUserConnection,
    ):
        self._create_user = create_user
        self._get_all_users = get_all_users
        self._delete_user = delete_user
        self._update_user = update_user
        self._get_user_by_username = get_user_by_username
        self._count_user_connection = count_user_connection

        self._users: t.List[UserConsole] = []

        self.console = Console('GERENCIADOR DE USUÁRIOS')

    @property
    def users(self) -> t.List[UserConsole]:
        if not self._users:
            self._users.extend(
                [UserConsole.create(user.to_dict()) for user in self._get_all_users.execute()]
            )
        return self._users

    def run(self) -> None:
        self.console.append_item(
            FuncItem(
                'CRIAR USUÁRIO',
                lambda: CreateUserCallback(
                    self._create_user,
                    self._get_user_by_username,
                    self.users,
                    UserInputData(),
                )(),
            ),
        )
        self.console.append_item(
            FuncItem(
                'GERAR USUÁRIO',
                lambda: CreateUserCallback(
                    self._create_user,
                    self._get_user_by_username,
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
                        self._delete_user,
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
                        self._update_user,
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
                        self._update_user,
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
                        self._update_user,
                        self.users,
                    ),
                ).start,
            )
        )

        self.console.append_item(
            FuncItem(
                'MONITORAMENTO',
                MonitorCallback(
                    self._count_user_connection,
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
