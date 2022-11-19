import typing as t

from app.terminal.console.common import Callback
from app.terminal.console.user.console import UserConsole
from app.utilities.logger import logger
from console.console import Console, FuncItem
from console.formatter import Formatter


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


class ConsoleDeleteUUID(ConsoleUUID):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Remover UUID'


class ConsoleListUUID(ConsoleUUID):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Listar UUID'
