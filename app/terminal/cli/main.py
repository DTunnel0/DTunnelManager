import argparse

from .account.create import AccountCreate
from .account.view import ViewAccount

# parser = argparse.ArgumentParser(prog='app', description='App CLI')
# subparsers = parser.add_subparsers()


class MainCLI:
    def __init__(
        self,
        create_account_controller,
        get_user_controller,
    ) -> None:
        self.create_account_controller = create_account_controller
        self.get_user_controller = get_user_controller

        self.parser = argparse.ArgumentParser(prog='app', description='App CLI')
        self.subparsers = self.parser.add_subparsers(dest='command')

        self.account_create = AccountCreate(
            self.create_account_controller,
            self.subparsers.add_parser('create', description='Create a new account'),
        )
        self.account_view = ViewAccount(
            self.get_user_controller,
            self.subparsers.add_parser('view', description='View an account'),
        )

    def start(self, _args: list) -> None:
        args = self.parser.parse_args(_args)

        if args.command == 'create':
            self.account_create.run(args)

        if args.command == 'view':
            self.account_view.run(args)
