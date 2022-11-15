# flake8: noqa

from typing import NamedTuple, Union

from console.colors import bg_color_name, color_name

from ..interfaces.presenter import Presenter


class UserConsoleModel(NamedTuple):
    username: str
    password: str
    connection_limit: int
    expiration_date: str
    v2ray_uuid: Union[None, str]


class CreateUserConsolePresenter(Presenter):
    def present(self, model: UserConsoleModel) -> str:
        return self.__build_message(model)

    def __build_message(self, model: UserConsoleModel) -> str:
        title = self.__build_title()
        message = self.__build_user_message(model)
        return title + message

    def __build_title(self) -> str:
        title = '✅USUARIO CRIADO COM SUCESSO✅'
        text_size = len(title) + 2
        line_size = (50 - text_size) // 2

        return (
            '\n'
            + color_name.WHITE
            + '━' * 50
            + color_name.END
            + '\n'
            + bg_color_name.GREEN
            + ' ' * line_size
            + title
            + ' ' * line_size
            + color_name.END
            + '\n'
            + color_name.WHITE
            + '━' * 50
            + color_name.END
            + '\n'
        )

    def __build_user_message(self, model: UserConsoleModel) -> str:
        message = (
            color_name.WHITE
            + '👤Nome do usuario: '
            + color_name.END
            + color_name.BLUE
            + model.username
            + color_name.END
            + '\n'
            + color_name.WHITE
            + '🔑Senha: '
            + color_name.END
            + color_name.BLUE
            + model.password
            + color_name.END
            + '\n'
            + color_name.WHITE
            + '🔗Limite de conexoes: '
            + color_name.END
            + color_name.BLUE
            + str(model.connection_limit)
            + color_name.END
            + '\n'
            + color_name.WHITE
            + '📅Data de expiracao: '
            + color_name.END
            + color_name.BLUE
            + model.expiration_date
            + color_name.END
            + '\n'
            # + '━' * 50
            # + '\n'
        )

        if model.v2ray_uuid:
            message += (
                color_name.WHITE
                + '📡UUID do V2Ray: '
                + color_name.END
                + color_name.BLUE
                + model.v2ray_uuid
                + color_name.END
                + '\n'
            )

        message += color_name.WHITE + '━' * 50 + color_name.END + '\n'
        return message
