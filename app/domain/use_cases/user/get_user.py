from datetime import datetime
from typing import List, NamedTuple, Union

from app.domain.interfaces.user_repositoery import UserRepositoryInterface


class UserOutputDTO(NamedTuple):
    id: int
    username: str
    password: str
    v2ray_uuid: Union[None, str]
    connection_limit: int
    expiration_date: datetime

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'v2ray_uuid': self.v2ray_uuid,
            'connection_limit': self.connection_limit,
            'expiration_date': self.expiration_date,
        }


class GetUserUseCase:
    def __init__(self, repo: UserRepositoryInterface):
        self.__repo = repo

    def execute(self, id: int) -> UserOutputDTO:
        user = self.__repo.get_by_id(id)
        return UserOutputDTO(
            id=id,
            username=user.username,
            password=user.password,
            v2ray_uuid=user.v2ray_uuid,
            connection_limit=user.connection_limit,
            expiration_date=user.expiration_date,
        )


class GetUserByUsernameUseCase:
    def __init__(self, repo: UserRepositoryInterface):
        self.__repo = repo

    def execute(self, username: str) -> UserOutputDTO:
        user = self.__repo.get_by_username(username)
        return UserOutputDTO(
            id=user.id or -1,
            username=user.username,
            password=user.password,
            v2ray_uuid=user.v2ray_uuid,
            connection_limit=user.connection_limit,
            expiration_date=user.expiration_date,
        )


class GetUserByUUIDUseCase:
    def __init__(self, repo: UserRepositoryInterface):
        self.__repo = repo

    def execute(self, uuid: str) -> UserOutputDTO:
        user = self.__repo.get_by_uuid(uuid)
        return UserOutputDTO(
            id=user.id or -1,
            username=user.username,
            password=user.password,
            v2ray_uuid=user.v2ray_uuid,
            connection_limit=user.connection_limit,
            expiration_date=user.expiration_date,
        )


class GetAllUsersUseCase:
    def __init__(self, repo: UserRepositoryInterface):
        self.__repo = repo

    def execute(self) -> List[UserOutputDTO]:
        users = self.__repo.get_all()
        return [
            UserOutputDTO(
                id=user.id,
                username=user.username,
                password=user.password,
                v2ray_uuid=user.v2ray_uuid,
                connection_limit=user.connection_limit,
                expiration_date=user.expiration_date,
            )
            for user in users
            if user.id
        ]
