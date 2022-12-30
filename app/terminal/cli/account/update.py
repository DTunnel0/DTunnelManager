from argparse import ArgumentParser
from datetime import datetime, timedelta
from typing import Any

from app.domain.use_cases.user.update_user import UpdateUserUseCase, UserUpdateInputDTO
from app.domain.use_cases.user.get_user import GetUserByUsernameUseCase


class UpdateUser:
    def __init__(
        self,
        update_user: UpdateUserUseCase,
        get_user: GetUserByUsernameUseCase,
        parser: ArgumentParser,
    ) -> None:
        self.update_user = update_user
        self.get_user = get_user
        self.parser = parser
        self.parser.add_argument(
            '-u',
            '--username',
            help='Username',
            type=str,
            required=True,
        )
        self.parser.add_argument(
            '-p',
            '--password',
            help='Password',
            type=str,
        )
        self.parser.add_argument(
            '-l',
            '--limit-connections',
            type=int,
            default=1,
            help='Limit connections (default: %(default)s)',
        )
        self.parser.add_argument(
            '-e',
            '--expiration-date',
            type=str,
            default=(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
            help='Expiration date (default: %(default)s)',
        )

    def __parse_expiration_date(self, date: str) -> datetime:
        try:
            if date.isdigit():
                return datetime.now() + timedelta(days=int(date))
            return datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            raise ValueError('Invalid expiration date')

    def run(self, args: Any) -> None:
        try:
            user = self.get_user.execute(username=args.username)
            expiration_date = self.__parse_expiration_date(args.expiration_date)
            self.update_user.execute(
                UserUpdateInputDTO(
                    id=user.id,
                    username=args.username,
                    password=args.password,
                    connection_limit=args.limit_connections,
                    expiration_date=expiration_date,
                )
            )
            print('User updated')
        except Exception as e:
            print('Error: {error}'.format(error=e))
            exit(1)
