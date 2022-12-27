import datetime
import uuid
from typing import Union


class UUID(str):
    def __new__(cls, value: str) -> 'UUID':
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValueError('Invalid UUID')

        return super().__new__(cls, value)


class Username(str):
    def __new__(cls, value: str) -> 'Username':
        if len(value) < 3:
            raise ValueError('Username must be at least 3 characters long')

        return super().__new__(cls, value)


class Password(str):
    def __new__(cls, value: str) -> 'Password':
        if len(value) < 4:
            raise ValueError('Password must be at least 4 characters long')

        return super().__new__(cls, value)


class ConnectionLimit(int):
    def __new__(cls, value: int) -> 'ConnectionLimit':
        if value <= 0:
            raise ValueError('Limit is invalid')

        return super().__new__(cls, value)


class User:
    id: Union[None, int]
    username: Username
    password: Password
    v2ray_uuid: Union[UUID, None]
    connection_limit: ConnectionLimit
    expiration_date: datetime.datetime

    def __init__(
        self,
        username: Username,
        password: Password,
        v2ray_uuid: Union[UUID, None],
        connection_limit: ConnectionLimit,
        expiration_date: datetime.datetime,
        id: Union[None, int] = None,
    ):
        self.username = username
        self.password = password
        self.v2ray_uuid = v2ray_uuid
        self.connection_limit = connection_limit
        self.expiration_date = expiration_date
        self.id = id

    @staticmethod
    def create(data: dict) -> 'User':
        return User(
            id=data.get('id'),
            username=Username(data['username']),
            password=Password(data['password']),
            connection_limit=ConnectionLimit(data['connection_limit']),
            expiration_date=data['expiration_date'],
            v2ray_uuid=UUID(data['v2ray_uuid']) if data['v2ray_uuid'] else None,
        )

    def is_expired(self) -> bool:
        return self.expiration_date < datetime.datetime.now()
