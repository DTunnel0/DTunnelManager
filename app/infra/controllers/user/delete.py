from app.domain.use_cases.user.delete_user import DeleteUserUseCase


class DeleteUserController:
    def __init__(self, delete_user_use_case: DeleteUserUseCase):
        self.delete_user_use_case = delete_user_use_case

    def handle(self, user_id: int) -> None:
        self.delete_user_use_case.execute(user_id)
