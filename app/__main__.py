from .data.gateway.user import SystemUserGateway
from .data.repositories.user import UserRepository
from .domain.use_cases.user.create_user import CreateUserUseCase
from .domain.use_cases.user.update_user import UpdateUserUseCase
from .domain.use_cases.user.count_connections import CountUserConnection
from .domain.use_cases.user.delete_user import DeleteUserUseCase, DeleteUserByUsernameUseCase
from .domain.use_cases.user.get_user import (
    GetAllUsersUseCase,
    GetUserByUsernameUseCase,
    GetUserByUUIDUseCase,
)
from .terminal import terminal_main

gateway = SystemUserGateway()
repository = UserRepository()

create_user_use_case = CreateUserUseCase(repository, gateway)
get_user_by_uuid_use_case = GetUserByUUIDUseCase(repository)
get_all_users_use_case = GetAllUsersUseCase(repository)
delete_user_use_case = DeleteUserUseCase(repository, gateway)
delete_user_by_username_use_case = DeleteUserByUsernameUseCase(repository, gateway)
update_user_use_case = UpdateUserUseCase(repository, gateway)
get_user_by_username_use_case = GetUserByUsernameUseCase(repository)
count_user_connection_use_case = CountUserConnection(gateway)


def main():
    terminal_main(
        create_user_use_case,
        get_user_by_uuid_use_case,
        get_all_users_use_case,
        delete_user_use_case,
        delete_user_by_username_use_case,
        update_user_use_case,
        get_user_by_username_use_case,
        count_user_connection_use_case,
    )


if __name__ == '__main__':
    main()
