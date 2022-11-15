import json

from argparse import ArgumentParser
from typing import Any

from app.infra.controllers.get_user import GetUserByUsernameController


class ViewAccount:
    def __init__(
        self,
        get_user_controller: GetUserByUsernameController,
        parser: ArgumentParser,
    ) -> None:
        self.get_user_controller = get_user_controller
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
            data = self.get_user_controller.handle(username=args.username)
            if args.json:
                self.__print_json(data)
            else:
                self.__print_default(data)
        except Exception as e:
            print(e)
            exit(1)

    def __print_json(self, data: dict) -> None:
        print(json.dumps(data, indent=4))

    def __print_default(self, data: dict) -> None:
        for key, value in data.items():
            print('{key}: {value}'.format(key=key, value=value))
