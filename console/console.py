#!/usr/bin/env python3

import os
from .utils import pause
from .formatter import Formatter
from .colors import color_name


class Console:
    def __init__(self, title, text_exit='SAIR', formatter=Formatter()):
        self.title = title
        self.items = []
        self.exit_item = ExitItem(text_exit)
        self.selected_exit = False

        self.item_returned = None
        self.item_selected = None

        self.input_text = 'Escolha uma opcao: '
        self.formatter = formatter

        self._exit = False

    def append_item(self, item: 'Item'):
        if self.items:
            del self.items[-1]

        self.items.append(item)
        if self.exit_item:
            self.items.append(self.exit_item)
        else:
            self.items.append(ExitItem())

    def remove_item(self, item):
        for idx, _item in enumerate(self.items):
            if _item == item:
                del self.items[idx]

    def select(self, idx):
        item_selected = self.items[idx]

        self.items[idx].index = idx
        self.item_returned = item_selected.action()
        self.selected_exit = item_selected.shuld_exit
        self._exit = item_selected.exit_on_select

    def user_input(self):
        return input(
            '{red}{text}{reset}'.format_map(
                {'red': color_name.RED, 'text': self.input_text, 'reset': color_name.RESET}
            )
        )

    def select_item_name(self, name) -> int:
        for item in self.items:
            if name in item.text:
                return self.items.index(item)
        return -1

    def process_user_input(self):
        user_input = self.user_input()

        try:
            num = int(user_input)
        except ValueError:
            return

        if -1 < num < len(self.items):
            self.select(num - 1)
            return

        idx = self.select_item_name(user_input)
        if idx != -1:
            self.select(idx)

    def print_items(self):
        print(self.formatter.formatter(self.items, self.title))

    def show(self):
        while not self.selected_exit and self.items[:-1] and not self._exit:
            self.clear_screen()
            self.print_items()
            self.process_user_input()

    def exit(self):
        self._exit = True
        self.selected_exit = True

    @staticmethod
    def clear_screen():
        os.system('clear' if os.name == 'posix' else 'cls')

    @staticmethod
    def pause(message: str = 'Enter para continuar'):
        print(color_name.GREEN + message + color_name.RESET, end='')
        input()


class ConsoleUser(Console):
    def __init__(self, title):
        super(ConsoleUser, self).__init__(title=title, text_exit='VOLTAR')
        self.input_text = 'Escolha um usuario: '

    def get_index(self, choice):
        if choice.isnumeric() and -1 < int(choice) < len(self.items):
            return int(choice) - 1
        for item in self.items:
            if choice == item.text:
                return self.items.index(item)
        return None

    def process_user_input(self):
        user_input = self.user_input()
        try:
            choices = user_input.split()
            for choice in choices:
                idx = self.get_index(choice)
                if idx is not None:
                    self.select(idx)
            if idx is not None and -1 < idx < len(self.items):
                pause()
        except Exception as e:
            raise e

    def create_items(self, item, items):
        for user in items:
            self.append_item(item(user, self))

    def run(self, item, items):
        if self.item_returned is not None:
            self.item_returned = None

        self.selected_exit = False

        if not self.items:
            self.create_items(item, items)

        self.show()


class Item:
    def __init__(self, text, shuld_exit=False, exit_on_select=False):
        self.text = text
        self.shuld_exit = shuld_exit
        self.exit_on_select = exit_on_select
        self.is_exit_item = False

    def action(self):
        pass


class FuncItem(Item):
    def __init__(
        self,
        text,
        func,
        *args,
        shuld_exit=False,
        exit_on_select=False,
    ):
        super(FuncItem, self).__init__(text, shuld_exit, exit_on_select)
        self.func = func
        self.args = args

    def action(self):
        return self.func(*self.args)


class ExitItem(Item):
    def __init__(self, text='SAIR'):
        super(ExitItem, self).__init__(text, shuld_exit=True, exit_on_select=True)
        self.is_exit_item = True


def clear_screen():
    os.system('clear')
