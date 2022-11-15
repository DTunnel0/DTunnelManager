from app.terminal.console.utils import ConsoleUUID


class ConsoleDeleteUUID(ConsoleUUID):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Remover UUID'


class ConsoleListUUID(ConsoleUUID):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Listar UUID'
