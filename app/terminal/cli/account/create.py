from datetime import datetime, timedelta

from argparse import ArgumentParser
from typing import Any

from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO


class AccountCreate:
    def __init__(
        self,
        create_account: CreateUserUseCase,
        parser: ArgumentParser,
    ) -> None:
        self.create_account = create_account
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
            required=True,
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
            expiration_date = self.__parse_expiration_date(args.expiration_date)
            self.create_account.execute(
                UserInputDTO(
                    username=args.username,
                    password=args.password,
                    connection_limit=args.limit_connections,
                    expiration_date=expiration_date,
                )
            )
            print('Account created successfully')
        except Exception as e:
            print('Error: {error}'.format(error=e))
            exit(1)
