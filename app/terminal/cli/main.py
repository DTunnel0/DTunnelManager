import argparse

from .account.create import AccountCreate
from .account.view import ViewAccount, ViewAllAccounts
from .account.delete import DeleteUser
from .account.update import UpdateUser


class MainCLI:
    def __init__(
        self,
        create_account,
        get_user,
        get_all_users,
        update_user,
        delete_user,
    ) -> None:
        self.create_account = create_account
        self.get_user = get_user
        self.get_all_users = get_all_users
        self.update_user = update_user
        self.delete_user = delete_user

        self.parser = argparse.ArgumentParser(prog='app', description='App CLI')
        self.subparsers = self.parser.add_subparsers(dest='command')

        self.account_create = AccountCreate(
            self.create_account,
            self.subparsers.add_parser('create', description='Create a new account'),
        )
        self.account_view = ViewAccount(
            self.get_user,
            self.subparsers.add_parser('view', description='View a account'),
        )
        self.account_delete = DeleteUser(
            self.delete_user,
            self.subparsers.add_parser('delete', description='Delete a account'),
        )
        self.account_update = UpdateUser(
            self.update_user,
            self.get_user,
            self.subparsers.add_parser('update', description='Update a account'),
        )
        self.account_view_all = ViewAllAccounts(
            self.get_all_users,
            self.subparsers.add_parser('view-all', description='View all accounts'),
        )

    def start(self, _args: list) -> None:
        args = self.parser.parse_args(_args)

        if args.command == 'create':
            self.account_create.run(args)

        if args.command == 'view':
            self.account_view.run(args)

        if args.command == 'delete':
            self.account_delete.run(args)

        if args.command == 'update':
            self.account_update.run(args)

        if args.command == 'view-all':
            self.account_view_all.run(args)
