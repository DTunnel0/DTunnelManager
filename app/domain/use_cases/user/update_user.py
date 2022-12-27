from datetime import datetime
from typing import NamedTuple, Union

from app.domain.entities.user import UUID, ConnectionLimit, Password, Username
from app.domain.interfaces.user_gateway import UpdateUserInputGateway, UserGatewayInterface
from app.domain.interfaces.user_repositoery import UserRepositoryInterface


class UserUpdateInputDTO(NamedTuple):
    id: int
    username: Union[str, None] = None
    password: Union[str, None] = None
    v2ray_uuid: Union[str, None] = None
    connection_limit: Union[int, None] = None
    expiration_date: Union[datetime, None] = None


class UpdateUserUseCase:
    def __init__(self, repo: UserRepositoryInterface, gateway: UserGatewayInterface) -> None:
        self.__repo = repo
        self.__gateway = gateway

    def execute(self, input: UserUpdateInputDTO) -> None:
        user = self.__repo.get_by_id(input.id)

        if input.username is not None:
            user.username = Username(input.username)

        if input.password is not None:
            user.password = Password(input.password)

        if input.v2ray_uuid is not None:
            user.v2ray_uuid = UUID(input.v2ray_uuid) if input.v2ray_uuid else None

        if input.connection_limit is not None:
            user.connection_limit = ConnectionLimit(input.connection_limit)

        if input.expiration_date is not None:
            user.expiration_date = input.expiration_date

        self.__gateway.update(
            UpdateUserInputGateway(
                username=input.username,
                password=input.password,
                expiration_date=input.expiration_date
                and input.expiration_date.strftime('%Y-%m-%d')  # noqa
                or None,  # noqa
            )
        )
        self.__repo.update(user)
