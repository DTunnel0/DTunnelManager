import typing as t

from app.domain.use_cases.user.get_user import GetAllUsersUseCase
from app.domain.use_cases.user.get_user import GetUserByUUIDUseCase
from app.domain.use_cases.user.update_user import UpdateUserUseCase
from app.domain.use_cases.user.delete_user import DeleteUserUseCase

from app.terminal.console.user.console import UserConsole, UserMenuConsole
from app.terminal.console.v2ray.console import ConsoleDeleteUUID, ConsoleListUUID
from console.console import Console, FuncItem

from .callback import (
    V2RayChangePortCallback,
    V2RayConfigCallback,
    V2RayCreateUUIDCallback,
    V2RayInstallCallback,
    V2RayRemoveUUIDCallback,
    V2RayRestartCallback,
    V2RayStartCallback,
    V2RayStopCallback,
    V2RayUninstallCallback,
    V2RayUUIDListCallback,
)
from .utils.manager import V2RayManager


class MainV2rayConsole:
    def __init__(
        self,
        get_all_users: GetAllUsersUseCase,
        get_user_by_uuid: GetUserByUUIDUseCase,
        update_user: UpdateUserUseCase,
    ) -> None:
        self.get_all_users = get_all_users
        self.get_user_by_uuid = get_user_by_uuid
        self.update_user = update_user

        self.console = Console('V2Ray Manager')
        self.v2ray_manager = V2RayManager()

        self._uuids: t.List[str] = []
        self._users: t.List[UserConsole] = []

    @property
    def uuids(self) -> t.List[str]:
        if not self._uuids:
            self._uuids.extend(self.v2ray_manager.get_clients())
        return self._uuids

    @property
    def users(self) -> t.List[UserConsole]:
        if not self._users:
            self._users = UserConsole.collection(
                [u.to_dict() for u in self.get_all_users.execute()],
            )
        return self._users

    def run(self) -> None:
        if not self.v2ray_manager.is_installed():
            self.console.append_item(
                FuncItem(
                    'INSTALAR V2RAY',
                    V2RayInstallCallback(
                        self.v2ray_manager,
                    ),
                    self.start,
                    shuld_exit=True,
                )
            )
            self.console.show()
            return

        if not V2RayManager.is_running():
            self.console.append_item(
                FuncItem(
                    'INICIAR V2RAY',
                    V2RayStartCallback(
                        self.v2ray_manager,
                    ),
                    self.start,
                    shuld_exit=True,
                )
            )
        else:
            self.console.append_item(
                FuncItem(
                    'PARAR V2RAY',
                    V2RayStopCallback(
                        self.v2ray_manager,
                    ),
                    self.start,
                    shuld_exit=True,
                )
            )
            self.console.append_item(
                FuncItem(
                    'REINICIAR V2RAY',
                    V2RayRestartCallback(
                        self.v2ray_manager,
                    ),
                    self.start,
                    shuld_exit=True,
                )
            )

        self.console.append_item(
            FuncItem(
                'ALTERAR PORTA',
                V2RayChangePortCallback(self.v2ray_manager),
            )
        )
        self.console.append_item(
            FuncItem(
                'CRIAR NOVO UUID',
                V2RayCreateUUIDCallback(self.uuids, self.v2ray_manager),
            ),
        )

        self.console.append_item(
            FuncItem(
                'REMOVER UUID',
                lambda: ConsoleDeleteUUID(
                    self.uuids,
                    self.users,
                    V2RayRemoveUUIDCallback(
                        self.uuids,
                        self.users,
                        self.update_user,
                        self.v2ray_manager,
                    ),
                ).start(),
            )
        )
        self.console.append_item(
            FuncItem(
                'LISTAR UUID\'S',
                lambda: ConsoleListUUID(
                    self.uuids,
                    self.users,
                    V2RayUUIDListCallback(
                        UserMenuConsole(self.users),
                        self.update_user,
                        self.v2ray_manager,
                    ),
                ).start(),
            )
        )
        self.console.append_item(
            FuncItem(
                'VER CONFIG. V2RAY',
                V2RayConfigCallback(self.v2ray_manager),
            )
        )
        self.console.append_item(
            FuncItem(
                'DESINSTALAR V2RAY',
                V2RayUninstallCallback(self.v2ray_manager),
                self.start,
                shuld_exit=True,
            )
        )
        self.console.show()

    def start(self) -> None:
        self.console._exit = False
        self.console.selected_exit = False
        self.console.items.clear()
        self.run()
