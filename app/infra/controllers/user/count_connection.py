from app.domain.use_cases.user.count_connections import CountUserConnection


class CountUserConnectionController:
    def __init__(self, use_case: CountUserConnection) -> None:
        self.use_case = use_case

    def handle(self, username: str) -> int:
        return self.use_case.execute(username)
