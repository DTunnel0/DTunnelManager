from .data.gateway.user import SystemUserGateway
from .data.repositories.user import UserRepository
from .domain.use_cases.user.count_connections import CountUserConnection
from .domain.use_cases.user.create_user import CreateUserUseCase
from .domain.use_cases.user.delete_user import DeleteUserUseCase
from .domain.use_cases.user.get_user import (
    GetAllUsersUseCase,
    GetUserByUsernameUseCase,
    GetUserByUUIDUseCase,
)
from .domain.use_cases.user.update_user import UpdateUserUseCase
from .infra.controllers.user.count_connection import CountUserConnectionController
from .infra.controllers.user.create import CreateUserController
from .infra.controllers.user.delete import DeleteUserController
from .infra.controllers.user.get_all import GetAllUsersController
from .infra.controllers.user.get_user import (
    GetUserByUsernameController,
    GetUserByUUIDController,
)
from .infra.controllers.user.update import UpdateUserController
from .infra.presenters.console import CreateUserConsolePresenter
from .terminal import terminal_main

gateway = SystemUserGateway()
repository = UserRepository()

create_user_use_case = CreateUserUseCase(repository, gateway)
get_user_by_uuid_use_case = GetUserByUUIDUseCase(repository)
get_all_users_use_case = GetAllUsersUseCase(repository)
delete_user_use_case = DeleteUserUseCase(repository, gateway)
update_user_use_case = UpdateUserUseCase(repository, gateway)
get_user_by_username_use_case = GetUserByUsernameUseCase(repository)
count_user_connection_use_case = CountUserConnection(gateway)

create_user_controller = CreateUserController(create_user_use_case, CreateUserConsolePresenter())
get_all_users_controller = GetAllUsersController(get_all_users_use_case)
get_user_by_username_controller = GetUserByUsernameController(get_user_by_username_use_case)
get_user_by_uuid_controller = GetUserByUUIDController(get_user_by_uuid_use_case)
delete_user_controller = DeleteUserController(delete_user_use_case)
update_user_controller = UpdateUserController(update_user_use_case)
count_user_connection_controller = CountUserConnectionController(count_user_connection_use_case)


def main():
    terminal_main(
        create_user_controller,
        get_all_users_controller,
        delete_user_controller,
        update_user_controller,
        get_user_by_username_controller,
        count_user_connection_controller,
        get_user_by_uuid_controller,
    )


if __name__ == '__main__':
    main()
