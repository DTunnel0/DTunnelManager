import datetime
from typing import Any

from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO
from app.infra.interfaces.presenter import Presenter
from app.infra.presenters.console import UserConsoleModel


class CreateUserController:
    def __init__(self, use_case: CreateUserUseCase, presenter: Presenter):
        self.__use_case = use_case
        self.__presenter = presenter

    def __parse_date(self, date: str) -> datetime.datetime:
        try:
            return datetime.datetime.fromisoformat(date)
        except AttributeError:
            return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')

    def handle(self, data: dict) -> Any:
        user_input_dto = UserInputDTO(
            username=data['username'],
            password=data['password'],
            connection_limit=data['connection_limit'],
            expiration_date=self.__parse_date(data['expiration_date']),
        )
        self.__use_case.execute(user_input_dto)
        return self.__presenter.present(
            UserConsoleModel(
                username=user_input_dto.username,
                password=user_input_dto.password,
                connection_limit=user_input_dto.connection_limit,
                expiration_date=user_input_dto.expiration_date.strftime('%d/%m/%Y'),
                v2ray_uuid=user_input_dto.v2ray_uuid,
            )
        )
