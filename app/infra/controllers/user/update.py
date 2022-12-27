from app.domain.use_cases.user.update_user import UpdateUserUseCase, UserUpdateInputDTO


class UpdateUserController:
    def __init__(self, update_user_use_case: UpdateUserUseCase):
        self.update_user_use_case = update_user_use_case

    def handle(self, data: dict) -> None:
        user_update_input_dto = UserUpdateInputDTO(**data)
        self.update_user_use_case.execute(user_update_input_dto)
