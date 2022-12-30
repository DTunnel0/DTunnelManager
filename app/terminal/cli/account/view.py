import json

from argparse import ArgumentParser
from typing import Any

from app.domain.use_cases.user.get_user import GetUserByUsernameUseCase, GetAllUsersUseCase


class ViewAccount:
    def __init__(
        self,
        get_user: GetUserByUsernameUseCase,
        parser: ArgumentParser,
    ) -> None:
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
            '-j',
            '--json',
            help='Print as JSON',
            action='store_true',
        )

    def run(self, args: Any) -> None:
        try:
            data = self.get_user.execute(username=args.username)
            if args.json:
                self.__print_json(data.to_dict())
            else:
                self.__print_default(data.to_dict())
        except Exception as e:
            print(e)
            exit(1)

    def __print_json(self, data: dict) -> None:
        print(json.dumps(data, indent=4))

    def __print_default(self, data: dict) -> None:
        for key, value in data.items():
            print('{key}: {value}'.format(key=key, value=value))


class ViewAllAccounts:
    def __init__(
        self,
        get_all_users: GetAllUsersUseCase,
        parser: ArgumentParser,
    ) -> None:
        self.get_all_users = get_all_users
        self.parser = parser
        self.parser.add_argument(
            '-j',
            '--json',
            help='Print as JSON',
            action='store_true',
        )

    def run(self, args: Any) -> None:
        try:
            data = self.get_all_users.execute()
            if args.json:
                self.__print_json([u.to_dict() for u in data])
            else:
                self.__print_default([u.to_dict() for u in data])
        except Exception as e:
            print(e)
            exit(1)

    def __print_json(self, data: list) -> None:
        print(json.dumps(data, indent=4))

    def __print_default(self, data: list) -> None:
        for user in data:
            print('-' * 80)
            for key, value in user.items():
                print('{key}: {value}'.format(key=key, value=value))
        print('-' * 80)
