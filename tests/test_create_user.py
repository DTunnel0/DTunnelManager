import datetime

from app.data.repositories.user import UserRepositoryImplInMemory
from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO
from app.domain.use_cases.user.get_user import GetUserUseCase
from app.domain.use_cases.user.update_user import UpdateUserUseCase, UserUpdateInputDTO


def test_create_user_of_30_days():
    repository = UserRepositoryImplInMemory()
    create_user_use_case = CreateUserUseCase(repository)
    get_user_use_case = GetUserUseCase(repository)

    user_id = 1000
    days = 30

    create_user_use_case.execute(
        UserInputDTO(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid='test',
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=days),
        )
    )

    user = get_user_use_case.execute(user_id)
    assert user_id == user.id
    assert (user.expiration_date - datetime.datetime.now()).days + 1 == days


def test_create_user_of_30_days_and_update_to_60_days():
    repository = UserRepositoryImplInMemory()
    create_user_use_case = CreateUserUseCase(repository)
    get_user_use_case = GetUserUseCase(repository)

    user_id = 1000
    days = 30

    create_user_use_case.execute(
        UserInputDTO(
            id=user_id,
            username='test',
            password='test',
            v2ray_uuid='test',
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=days),
        )
    )

    user = get_user_use_case.execute(user_id)
    assert user_id == user.id
    assert (user.expiration_date - datetime.datetime.now()).days + 1 == days

    days = 60
    update_user_use_case = UpdateUserUseCase(repository)
    update_user_use_case.execute(
        UserUpdateInputDTO(
            id=user_id,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=days),
        )
    )

    user = get_user_use_case.execute(user_id)
    assert user_id == user.id
    assert (user.expiration_date - datetime.datetime.now()).days + 1 == days
    assert user.username == 'test'
