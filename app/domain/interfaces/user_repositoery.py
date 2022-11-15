from abc import ABCMeta, abstractmethod
from typing import List

from app.domain.entities.user import User


class UserRepositoryInterface(metaclass=ABCMeta):
    @abstractmethod
    def create(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[User]:
        raise NotImplementedError
