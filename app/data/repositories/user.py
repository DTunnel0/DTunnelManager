import typing as t

from app.data.config import DBConnection
from app.domain.entities import User
from app.data.models.user import User as UserModel

from app.domain.interfaces.user_repositoery import UserRepositoryInterface


class UserRepositoryImplInMemory(UserRepositoryInterface):
    def __init__(self) -> None:
        self.__users: t.List[User] = []

    def create(self, user: User) -> None:
        for u in self.__users:
            if u.id == user.id:
                raise Exception('User already exists')

            if u.username == user.username:
                raise Exception('Username already exists')

        self.__users.append(user)

    def get_by_id(self, id: int) -> User:
        try:
            return next(filter(lambda u: u.id == id, self.__users))
        except StopIteration:
            raise Exception(f'User {id} not found')

    def get_by_uuid(self, uuid: str) -> User:
        try:
            return next(filter(lambda u: u.v2ray_uuid == uuid, self.__users))
        except StopIteration:
            raise Exception(f'User {uuid} not found')

    def get_by_username(self, username: str) -> User:
        try:
            return next(filter(lambda u: u.username == username, self.__users))
        except StopIteration:
            raise Exception(f'User {username} not found')

    def update(self, user: User) -> None:
        for i, u in enumerate(self.__users):
            if u.id == user.id:
                self.__users[i] = user
                return

        raise Exception(f'User {user.id} not found')

    def delete(self, user_id: int) -> None:
        for i, u in enumerate(self.__users):
            if u.id == user_id:
                del self.__users[i]
                return

        raise Exception(f'User {user_id} not found')

    def get_all(self) -> t.List[User]:
        return self.__users


class UserRepository(UserRepositoryInterface):
    def create(self, user: User) -> None:
        model = UserModel.of_entity(user)
        with DBConnection() as db:
            db.session.add(model)
            db.session.commit()
            db.session.refresh(model)

    def get_by_id(self, id: int) -> User:
        with DBConnection() as db:
            model = db.session.query(UserModel).filter(UserModel.id == id).first()
            if not model:
                raise Exception('User not found')
            return model.to_entity()

    def get_by_username(self, username: str) -> User:
        with DBConnection() as db:
            model = db.session.query(UserModel).filter(UserModel.username == username).first()
            if not model:
                raise Exception('User not found')
            return model.to_entity()

    def get_by_uuid(self, uuid: str) -> User:
        with DBConnection() as db:
            model = db.session.query(UserModel).filter(UserModel.v2ray_uuid == uuid).first()
            if not model:
                raise Exception('User not found')
            return model.to_entity()

    def get_all(self) -> t.List[User]:
        with DBConnection() as db:
            models = db.session.query(UserModel).all()
            return [model.to_entity() for model in models]

    def update(self, user: User) -> None:
        model = UserModel.of_entity(user)
        with DBConnection() as db:
            db.session.merge(model)
            db.session.commit()
            # db.session.refresh(model)

    def delete(self, user_id: int) -> None:
        with DBConnection() as db:
            user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
            db.session.delete(user)
            db.session.commit()
