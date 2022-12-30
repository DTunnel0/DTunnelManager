import sys

from typing import List

from app.domain.use_cases.user.count_connections import CountUserConnection
from app.domain.use_cases.user.create_user import CreateUserUseCase
from app.domain.use_cases.user.delete_user import DeleteUserUseCase, DeleteUserByUsernameUseCase
from app.domain.use_cases.user.get_user import (
    GetAllUsersUseCase,
    GetUserByUsernameUseCase,
    GetUserByUUIDUseCase,
)
from app.domain.use_cases.user.update_user import UpdateUserUseCase

from app.utilities.logger import logger

from .console.badvpn.main import MainBadVpnConsole
from .console.openvpn.main import MainOpenVPNConsole
from .console.v2ray.main import MainV2rayConsole
from .console.socks.main import MainSocksConsole
from .console.tools.main import MainToolsConsole
from .console.user.main import MainUserConsole

from .cli.main import MainCLI

from console.console import Console, FuncItem


def make_user_console_main(
    create_user: CreateUserUseCase,
    get_all_users: GetAllUsersUseCase,
    delete_user: DeleteUserUseCase,
    update_user: UpdateUserUseCase,
    get_user_by_username: GetUserByUsernameUseCase,
    count_user_connection: CountUserConnection,
) -> MainUserConsole:
    return MainUserConsole(
        create_user,
        get_all_users,
        delete_user,
        update_user,
        get_user_by_username,
        count_user_connection,
    )


def connection_choices(
    get_all_users: GetAllUsersUseCase,
    get_user_by_uuid: GetUserByUUIDUseCase,
    update_user: UpdateUserUseCase,
) -> None:
    console = Console('GERENCIADOR DE CONEXÕES')
    console.append_item(FuncItem('SOCKS HTTP', MainSocksConsole('http').start))
    console.append_item(FuncItem('SOCKS SSL', MainSocksConsole('https').start))
    console.append_item(FuncItem('OPENVPN', MainOpenVPNConsole().start))
    console.append_item(
        FuncItem(
            'V2RAY',
            MainV2rayConsole(
                get_all_users,
                get_user_by_uuid,
                update_user,
            ).start,
        )
    )
    console.append_item(FuncItem('BADUDP', MainBadVpnConsole().start))
    console.show()


def console(
    create_user: CreateUserUseCase,
    get_all_users: GetAllUsersUseCase,
    delete_user: DeleteUserUseCase,
    update_user: UpdateUserUseCase,
    get_user_by_username: GetUserByUsernameUseCase,
    count_user_connection: CountUserConnection,
    get_user_by_uuid: GetUserByUUIDUseCase,
) -> None:
    console = Console('GERENCIADOR')
    console.append_item(
        FuncItem(
            'GERENCIADOR DE USUÁRIOS',
            make_user_console_main(
                create_user,
                get_all_users,
                delete_user,
                update_user,
                get_user_by_username,
                count_user_connection,
            ).start,
        )
    )
    console.append_item(
        FuncItem(
            'GERENCIADOR DE CONEXÕES',
            connection_choices,
            get_all_users,
            get_user_by_uuid,
            update_user,
        )
    )
    console.append_item(
        FuncItem(
            'GERENCIADOR DE FERRAMENTS',
            MainToolsConsole(create_user).start,
        )
    )
    console.append_item(
        FuncItem(
            'GERENCIADOR DO PAINEL',
            input,
        )
    )

    try:
        console.show()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Até mais!')


def cli(
    args: List[str],
    create_user: CreateUserUseCase,
    get_user_by_username: GetUserByUsernameUseCase,
    get_all_users: GetAllUsersUseCase,
    update_user: UpdateUserUseCase,
    delete_user: DeleteUserByUsernameUseCase,
):
    cli = MainCLI(
        create_user,
        get_user_by_username,
        get_all_users,
        update_user,
        delete_user,
    )
    cli.start(args)


def terminal_main(
    create_user_use_case: CreateUserUseCase,
    get_user_by_uuid_use_case: GetUserByUUIDUseCase,
    get_all_users_use_case: GetAllUsersUseCase,
    delete_user_use_case: DeleteUserUseCase,
    delete_user_by_username_use_case: DeleteUserByUsernameUseCase,
    update_user_use_case: UpdateUserUseCase,
    get_user_by_username_use_case: GetUserByUsernameUseCase,
    count_user_connection_use_case: CountUserConnection,
) -> None:
    args = sys.argv[1:]
    if args:
        cli(
            args,
            create_user_use_case,
            get_user_by_username_use_case,
            get_all_users_use_case,
            update_user_use_case,
            delete_user_by_username_use_case,
        )
    else:
        console(
            create_user_use_case,
            get_all_users_use_case,
            delete_user_use_case,
            update_user_use_case,
            get_user_by_username_use_case,
            count_user_connection_use_case,
            get_user_by_uuid_use_case,
        )
