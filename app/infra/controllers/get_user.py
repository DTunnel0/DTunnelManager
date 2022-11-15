from app.domain.use_cases.user.get_user import GetUserByUUIDUseCase, GetUserByUsernameUseCase


class GetUserByUsernameController:
    def __init__(self, use_case: GetUserByUsernameUseCase):
        self.__use_case = use_case

    def handle(self, username: str) -> dict:
        data = self.__use_case.execute(username).to_dict()
        data['expiration_date'] = data['expiration_date'].isoformat(timespec='seconds', sep=' ')
        return data


class GetUserByUUIDController:
    def __init__(self, use_case: GetUserByUUIDUseCase):
        self.__use_case = use_case

    def handle(self, uuid: str) -> dict:
        data = self.__use_case.execute(uuid).to_dict()
        data['expiration_date'] = data['expiration_date'].isoformat(timespec='seconds', sep=' ')
        return data
