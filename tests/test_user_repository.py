import pytest
import datetime
import uuid

from app.data.repositories.user import UserRepository
from app.domain.entities.user import User


@pytest.mark.skip(reason='Not implemented')
def test_deve_criar_usuario_e_salvar_no_banco_de_dados():
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=1000,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user = user_repository.get_by_id(1000)
    assert user.username == 'test'


@pytest.mark.skip(reason='Not implemented')
def test_deve_atualizar_usuario_e_salvar_no_banco_de_dados():
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=1000,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user = user_repository.get_by_id(1000)
    user.username = 'test2'
    user_repository.update(user)

    user = user_repository.get_by_id(1000)
    assert user.username == 'test2'


def test_deve_deletar_usuario_e_salvar_no_banco_de_dados():
    user_repository = UserRepository()
    user_repository.create(
        User(
            id=1000,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        )
    )

    user_repository.delete(1000)
    with pytest.raises(Exception):
        user_repository.get_by_id(1000)
