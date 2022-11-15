from typing import List
from app.domain.use_cases.user.get_user import GetAllUsersUseCase, UserOutputDTO


class GetAllUsersController:
    def __init__(self, get_all_users_use_case: GetAllUsersUseCase):
        self.get_all_users_use_case = get_all_users_use_case

    def handle(self) -> List[UserOutputDTO]:
        users = self.get_all_users_use_case.execute()
        return users
