import datetime
import uuid

from app.data.repositories.user import UserRepositoryImplInMemory
from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO
from app.domain.use_cases.user.get_user import GetUserUseCase
from app.domain.use_cases.user.update_user import UpdateUserUseCase, UserUpdateInputDTO


def test_deve_atualizar_um_usuario_de_30_dias_para_60_dias():
    repository = UserRepositoryImplInMemory()
    create_user_use_case = CreateUserUseCase(repository)
    get_user_use_case = GetUserUseCase(repository)
    update_user_use_case = UpdateUserUseCase(repository)

    user_id = 1000
    days = 30

    create_user_use_case.execute(
        UserInputDTO(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=days),
        )
    )

    update_user_use_case.execute(
        UserUpdateInputDTO(
            id=user_id,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=60),
        )
    )

    user = get_user_use_case.execute(user_id)
    assert (user.expiration_date - datetime.datetime.now()).days + 1 == 60


def test_dev_atualizar_um_usuario():
    repository = UserRepositoryImplInMemory()
    create_user_use_case = CreateUserUseCase(repository)
    get_user_use_case = GetUserUseCase(repository)
    update_user_use_case = UpdateUserUseCase(repository)

    user_id = 1000
    days = 30
    create_user_use_case.execute(
        UserInputDTO(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid=str(uuid.uuid4()),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=days),
        )
    )

    v2ray_uuid = str(uuid.uuid4())
    update_user_use_case.execute(
        UserUpdateInputDTO(
            id=user_id,
            username='test_01',
            password='1234',
            v2ray_uuid=v2ray_uuid,
            connection_limit=10,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=60),
        )
    )

    user = get_user_use_case.execute(user_id)
    assert user.username == 'test_01'
    assert user.password == '1234'
    assert user.v2ray_uuid == v2ray_uuid
    assert user.connection_limit == 10
