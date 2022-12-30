from datetime import datetime
from typing import NamedTuple, Union

from app.domain.entities.user import User
from app.domain.interfaces.user_gateway import CreateUserInputGateway, UserGatewayInterface
from app.domain.interfaces.user_repositoery import UserRepositoryInterface


class UserInputDTO(NamedTuple):
    username: str
    password: str
    connection_limit: int
    expiration_date: datetime
    v2ray_uuid: Union[None, str] = None

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'password': self.password,
            'v2ray_uuid': self.v2ray_uuid,
            'connection_limit': self.connection_limit,
            'expiration_date': self.expiration_date,
        }


class CreateUserUseCase:
    def __init__(self, repo: UserRepositoryInterface, gateway: UserGatewayInterface) -> None:
        self.__repo = repo
        self.__gateway = gateway

    def execute(self, input: UserInputDTO) -> None:
        user_id = self.__gateway.create(
            CreateUserInputGateway(
                username=input.username,
                password=input.password,
                expiration_date=input.expiration_date.strftime('%Y-%m-%d'),
            )
        )
        self.__repo.create(
            User.create(
                {
                    'id': user_id,
                    **input.to_dict(),
                }
            )
        )
