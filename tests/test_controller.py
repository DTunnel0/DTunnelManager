from unittest import mock

from app.infra.presenters.console import UserConsoleModel, CreateUserConsolePresenter
from app.infra.controllers.create_user import CreateUserController


def test_create_user_controller():
    use_case = mock.Mock()
    use_case.execute.return_value = None

    presenter = CreateUserConsolePresenter()
    controller = CreateUserController(use_case, presenter)
    response = controller.handle(
        {
            'username': 'test',
            'password': 'test',
            'connection_limit': 1,
            'expiration_date': '2022-01-01',
            'v2ray_uuid': 'test',
        }
    )
    assert isinstance(response, str)
