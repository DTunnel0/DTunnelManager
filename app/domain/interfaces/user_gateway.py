from typing import Union, NamedTuple
from abc import ABCMeta, abstractmethod


class CreateUserInputGateway(NamedTuple):
    username: str
    password: str
    expiration_date: str


class UpdateUserInputGateway(NamedTuple):
    username: Union[str, None]
    password: Union[str, None]
    expiration_date: Union[str, None]


class UserGatewayInterface(metaclass=ABCMeta):
    @abstractmethod
    def create(self, data: CreateUserInputGateway) -> int:
        raise NotImplementedError

    @abstractmethod
    def update(self, data: UpdateUserInputGateway) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, username: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_user_id(self, username: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def count_connections(self, username: str) -> int:
        raise NotImplementedError
