from typing import Any

from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO
from app.infra.interfaces.presenter import Presenter
from app.infra.presenters.console import UserConsoleModel


class CreateUserController:
    def __init__(self, use_case: CreateUserUseCase, presenter: Presenter):
        self.__use_case = use_case
        self.__presenter = presenter

    def handle(self, data: dict) -> Any:
        input = UserInputDTO(**data)
        self.__use_case.execute(input)
        return self.__presenter.present(
            UserConsoleModel(
                username=input.username,
                password=input.password,
                connection_limit=input.connection_limit,
                expiration_date=input.expiration_date.strftime('%d/%m/%Y'),
                v2ray_uuid=input.v2ray_uuid,
            )
        )
