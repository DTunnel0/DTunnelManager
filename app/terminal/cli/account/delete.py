from argparse import ArgumentParser
from typing import Any

from app.domain.use_cases.user.delete_user import DeleteUserByUsernameUseCase


class DeleteUser:
    def __init__(
        self,
        delte_user_use_case: DeleteUserByUsernameUseCase,
        parser: ArgumentParser,
    ) -> None:
        self.delte_user_use_case = delte_user_use_case
        self.parser = parser
        self.parser.add_argument(
            '-u',
            '--username',
            help='Username',
            type=str,
            required=True,
        )

    def run(self, args: Any) -> None:
        try:
            self.delte_user_use_case.execute(username=args.username)
            print('User deleted')
        except Exception as e:
            print(e)
            exit(1)
