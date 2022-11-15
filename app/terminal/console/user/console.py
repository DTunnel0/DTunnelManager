import typing as t
import datetime

from console import Console, FuncItem, Formatter
from console.colors import color_name


class UserConsole:
    def __init__(
        self,
        id: int,
        username: str,
        v2ray_uuid: t.Union[None, str],
        password: str,
        connection_limit: int,
        expiration_date: datetime.datetime,
    ):
        self.id = id
        self.username = username
        self.v2ray_uuid = v2ray_uuid
        self.password = password
        self.connection_limit = connection_limit
        self.expiration_date = expiration_date

    @staticmethod
    def create(data: dict) -> 'UserConsole':
        return UserConsole(
            id=data['id'],
            username=data['username'],
            v2ray_uuid=data['v2ray_uuid'],
            password=data['password'],
            connection_limit=data['connection_limit'],
            expiration_date=data['expiration_date'],
        )


class UserMenuConsole:
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Callable[[UserConsole], None],
        title: str = 'SELECIONE UM USUÁRIO',
    ):
        self._users = users
        self._on_select = on_select
        self._console = Console(title)

    @property
    def selected_exit(self) -> bool:
        return self._console.selected_exit

    def build_item_name(self, user: UserConsole) -> str:
        return user.username + ' ' * (self.width() - len(user.username))

    def __on_select(self, user: UserConsole) -> None:
        self._on_select(user)
        self.create_items()

    def create_items(self) -> None:
        self._console.items.clear()

        if not self._users:
            print(color_name.RED + 'Nenhum usuario foi encontrado.' + color_name.RESET)
            self._console.pause()
            self._console.exit()
            return

        for user in self._users:
            self._console.append_item(
                FuncItem(
                    self.build_item_name(user),
                    self.__on_select,
                    user,
                )
            )

    def width(self) -> int:
        width = [len(user.username) for user in self._users]
        return max(width)

    def start(self) -> None:
        self._console._exit = False
        self._console.selected_exit = False

        try:
            self.create_items()
            self._console.show()
        except KeyboardInterrupt:
            self._console.exit()


class UserMenuConsoleDeleteUser(UserMenuConsole):
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Callable[[UserConsole], None],
    ) -> None:
        super().__init__(users, on_select, 'EXCLUIR USUÁRIO')


class UserMenuConsolePassword(UserMenuConsole):
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Callable[[UserConsole], None],
    ) -> None:
        super().__init__(users, on_select, 'ALTERAR SENHA')
        self._console.formatter = Formatter(1)

    def build_item_name(self, user: UserConsole) -> str:
        width = self.width()
        return '{username:<{width}} - {password}'.format(
            username=user.username,
            password=user.password,
            width=width,
        )


class UserMenuConsoleConnectionLimit(UserMenuConsole):
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Callable[[UserConsole], None],
    ) -> None:
        super().__init__(users, on_select, 'ALTERAR LIMITE DE CONEXÕES')
        self._console.formatter = Formatter(1)

    def build_item_name(self, user: UserConsole) -> str:
        width = self.width()
        return '{username:<{width}} - {connection_limit:02d}'.format(
            username=user.username,
            connection_limit=user.connection_limit,
            width=width,
        )


class UserMenuConsoleExpirationDate(UserMenuConsole):
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Callable[[UserConsole], None],
    ):
        super().__init__(users, on_select, 'ALTERAR DATA DE EXPIRAÇÃO')
        self._console.formatter = Formatter(1)

    def build_item_name(self, user: UserConsole) -> str:
        width = self.width()
        return '{username:<{width}} - {expiration_date}'.format(
            username=user.username,
            expiration_date=user.expiration_date.strftime('%d/%m/%Y'),
            width=width,
        )
