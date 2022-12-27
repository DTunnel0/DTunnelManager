from app.infra.presenters.console import UserConsoleModel, CreateUserConsolePresenter


def test_console_presenter():
    model = UserConsoleModel(
        username='test',
        password='test',
        connection_limit=1,
        expiration_date='20/10/2022',
        v2ray_uuid='test',
    )

    presenter = CreateUserConsolePresenter()
    message = presenter.present(model)
    print(message)

    assert isinstance(message, str)
