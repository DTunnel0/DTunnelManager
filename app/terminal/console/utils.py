import datetime
import typing as t
from abc import ABCMeta, abstractmethod

from app.utilities.logger import logger
from console import Console, Formatter, FuncItem


class Callback(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> None:
        try:
            self.execute(*args, **kwargs)
        except Exception as e:
            logger.exception(e)


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

    @staticmethod
    def collection(data: t.List[dict]) -> t.List['UserConsole']:
        return list(map(UserConsole.create, data))


class UserMenuConsole:
    def __init__(
        self,
        users: t.List[UserConsole],
        on_select: t.Union[Callback, None] = None,
        title: str = 'SELECIONE UM USUÁRIO',
    ):
        self._users = users
        self._callback_on_select = on_select
        self._console = Console(title)

    def set_callback(self, on_select: Callback) -> None:
        self._callback_on_select = on_select

    @property
    def selected_exit(self) -> bool:
        return self._console.selected_exit

    def build_item_name(self, user: UserConsole) -> str:
        return user.username + ' ' * (self.width() - len(user.username))

    def __on_select(self, user: UserConsole) -> None:
        if self._callback_on_select:
            self._callback_on_select(user)
        self.create_items()

    def create_items(self) -> None:
        self._console.items.clear()

        if not self._users:
            logger.error('Nenhum usuario foi encontrado.')
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


class ConsoleUUID:
    def __init__(
        self,
        uuids: t.List[str],
        users: t.List[UserConsole],
        callback: t.Union[Callback, None] = None,
        title: str = 'V2Ray UUID',
    ) -> None:
        self.uuids = uuids
        self.users = users
        self.callback = callback
        self.title = title
        self.console = Console(
            title=self.title,
            formatter=Formatter(1),
        )

    def set_callback(self, callback: Callback) -> None:
        self.callback = callback

    def __get_user_by_uuid(self, uuid: str) -> t.Union[UserConsole, None]:
        for user in self.users:
            if user.v2ray_uuid == uuid:
                return user
        return None

    def __select_uuid(self, uuid: str, user: t.Union[UserConsole, None]) -> None:
        if self.callback:
            self.callback(uuid, user)
        self.console.items.clear()
        self.create_items()

    def create_items(self) -> None:
        if not self.uuids:
            logger.error('Nenhum UUID encontrado')
            Console.pause()
            return

        for uuid in self.uuids:
            text = '%s' % uuid
            user = self.__get_user_by_uuid(uuid)
            if user:
                text += ' - %s' % user.username

            self.console.append_item(FuncItem(text, self.__select_uuid, uuid, user))

    def start(self) -> None:
        self.console.items.clear()
        self.create_items()
        self.console.show()
