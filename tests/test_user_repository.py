import pytest
import datetime
import uuid

from app.data.repositories.user import UserRepository
from app.domain.entities.user import User


def test_deve_criar_um_usuario():
    user_id = 10001
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user = user_repository.get_by_id(user_id)
    assert user.username == 'test'

    user_repository.delete(user_id)


def test_deve_atualizar_um_usuario():
    user_id = 10001
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user = user_repository.get_by_id(user_id)
    user.username = 'test2'
    user_repository.update(user)

    user = user_repository.get_by_id(user_id)
    assert user.username == 'test2'

    user_repository.delete(user_id)


def test_deve_deletar_um_usuario():
    user_id = 10001
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user_repository.delete(user_id)
    with pytest.raises(Exception):
        user_repository.get_by_id(user_id)
