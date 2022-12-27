from sqlalchemy import String, DateTime, Column, Integer
from app.data.config import Base

from app.domain.entities import User as UserEntity


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    connection_limit = Column(Integer, nullable=False)
    expiration_date = Column(DateTime, nullable=False)

    v2ray_uuid = Column(String(50), nullable=True, unique=True)

    def __str__(self) -> str:
        return f'{self.id} - {self.username}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id}, {self.username})'

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            username=self.username,
            password=self.password,
            v2ray_uuid=self.v2ray_uuid,
            connection_limit=self.connection_limit,
            expiration_date=self.expiration_date,
        )

    @staticmethod
    def of_entity(user: UserEntity) -> 'User':
        return User(
            id=user.id,
            username=user.username,
            password=user.password,
            v2ray_uuid=user.v2ray_uuid,
            connection_limit=user.connection_limit,
            expiration_date=user.expiration_date,
        )
