import sys
from typing import List

from app.infra.controllers.user.count_connection import CountUserConnectionController
from app.infra.controllers.user.create import CreateUserController
from app.infra.controllers.user.delete import DeleteUserController
from app.infra.controllers.user.get_all import GetAllUsersController
from app.infra.controllers.user.get_user import GetUserByUUIDController, GetUserByUsernameController
from app.infra.controllers.user.update import UpdateUserController

from .console.badvpn.main import MainBadVpnConsole
from .console.openvpn.main import MainOpenVPNConsole
from .console.v2ray.main import MainV2rayConsole
from .console.socks.main import MainSocksConsole
from .console.tools.main import MainToolsConsole
from .console.user.main import MainUserConsole

from .cli.main import MainCLI

from app.utilities.logger import logger

from console.console import Console, FuncItem


def make_user_console_main(
    create_user_controller: CreateUserController,
    get_all_users_controller: GetAllUsersController,
    delete_user_controller: DeleteUserController,
    update_user_controller: UpdateUserController,
    get_user_by_username_controller: GetUserByUsernameController,
    count_user_connection_controller: CountUserConnectionController,
) -> MainUserConsole:
    return MainUserConsole(
        create_user_controller,
        get_all_users_controller,
        delete_user_controller,
        update_user_controller,
        get_user_by_username_controller,
        count_user_connection_controller,
    )


def connection_choices(
    get_all_users_controller: GetAllUsersController,
    get_user_by_uuid_controller: GetUserByUUIDController,
    update_user_controller: UpdateUserController,
) -> None:
    console = Console('GERENCIADOR DE CONEXÕES')
    console.append_item(FuncItem('SOCKS HTTP', MainSocksConsole('http').start))
    console.append_item(FuncItem('SOCKS SSL', MainSocksConsole('https').start))
    console.append_item(FuncItem('OPENVPN', MainOpenVPNConsole().start))
    console.append_item(
        FuncItem(
            'V2RAY',
            MainV2rayConsole(
                get_all_users_controller,
                get_user_by_uuid_controller,
                update_user_controller,
            ).start,
        )
    )
    console.append_item(FuncItem('BADUDP', MainBadVpnConsole().start))
    console.show()


def console(
    create_user_controller: CreateUserController,
    get_all_users_controller: GetAllUsersController,
    delete_user_controller: DeleteUserController,
    update_user_controller: UpdateUserController,
    get_user_by_username_controller: GetUserByUsernameController,
    count_user_connection_controller: CountUserConnectionController,
    get_user_by_uuid_controller: GetUserByUUIDController,
) -> None:
    console = Console('GERENCIADOR')
    console.append_item(
        FuncItem(
            'GERENCIADOR DE USUÁRIOS',
            make_user_console_main(
                create_user_controller,
                get_all_users_controller,
                delete_user_controller,
                update_user_controller,
                get_user_by_username_controller,
                count_user_connection_controller,
            ).start,
        )
    )
    console.append_item(
        FuncItem(
            'GERENCIADOR DE CONEXÕES',
            connection_choices,
            get_all_users_controller,
            get_user_by_uuid_controller,
            update_user_controller,
        )
    )
    console.append_item(
        FuncItem(
            'GERENCIADOR DE FERRAMENTS',
            MainToolsConsole(create_user_controller).start,
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
    create_user_controller: CreateUserController,
    get_user_by_username_controller: GetUserByUsernameController,
):
    cli = MainCLI(
        create_user_controller,
        get_user_by_username_controller,
    )
    cli.start(args)


def terminal_main(
    create_user_controller: CreateUserController,
    get_all_users_controller: GetAllUsersController,
    delete_user_controller: DeleteUserController,
    update_user_controller: UpdateUserController,
    get_user_by_username_controller: GetUserByUsernameController,
    count_user_connection_controller: CountUserConnectionController,
    get_user_by_uuid_controller: GetUserByUUIDController,
) -> None:
    args = sys.argv[1:]
    if args:
        cli(
            args,
            create_user_controller,
            get_user_by_username_controller,
        )
    else:
        console(
            create_user_controller,
            get_all_users_controller,
            delete_user_controller,
            update_user_controller,
            get_user_by_username_controller,
            count_user_connection_controller,
            get_user_by_uuid_controller,
        )
