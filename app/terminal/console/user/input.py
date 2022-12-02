import datetime
import random
import string
import typing as t

from console.colors import color_name


class Username:
    __size = 32
    __min_size = 4

    def __init__(self, value: t.Optional[str] = None) -> None:
        if value:
            self.__validate(value)
        self._value: t.Optional[str] = value

    @property
    def value(self) -> str:
        while not self._value:
            self._value = input(color_name.YELLOW + 'Nome de usuário: ' + color_name.RESET)
            try:
                self.__validate(self._value)
            except ValueError as e:
                print(color_name.RED + str(e) + color_name.RESET)
                self._value = None
        return self._value

    def __validate(self, value: str) -> None:
        if not value:
            raise ValueError('Nome de usuário não pode ser vazio.')

        if len(value) < self.__min_size:
            raise ValueError('Nome de usuário deve ter no mínimo 4 caracteres.')

        if len(value) > self.__size:
            raise ValueError('Nome de usuário deve ter no máximo 8 caracteres.')

        if value.count(' ') > 0:
            raise ValueError('Nome de usuário não pode conter espaços.')


class Password:
    __size = 32
    __min_size = 4

    def __init__(self, value: t.Optional[str] = None) -> None:
        if value:
            self.__validate(value)
        self._value: t.Optional[str] = value

    @property
    def value(self) -> str:
        while not self._value:
            self._value = input(color_name.YELLOW + 'Senha: ' + color_name.RESET)
            try:
                self.__validate(self._value)
            except ValueError as e:
                print(color_name.RED + str(e) + color_name.RESET)
                self._value = None
        return self._value

    def __validate(self, value: str) -> None:
        if not value:
            raise ValueError('Senha não pode ser vazia.')

        if len(value) < self.__min_size:
            raise ValueError('Senha deve ter no mínimo 4 caracteres.')

        if len(value) > self.__size:
            raise ValueError('Senha deve ter no máximo 8 caracteres.')

        if value.count(' ') > 0:
            raise ValueError('Senha não pode conter espaços.')


class ConnectionLimit:
    def __init__(self, value: t.Optional[int] = None) -> None:
        if value:
            self.__validate(value)
        self._value: t.Optional[int] = value

    @property
    def value(self) -> int:
        while not self._value:
            value = input(color_name.YELLOW + 'Limite de conexões: ' + color_name.RESET)
            try:
                self._value = int(value)
                self.__validate(self._value)
            except ValueError as e:
                print(color_name.RED + str(e) + color_name.RESET)
                self._value = None
        return int(self._value)

    def __validate(self, value: int) -> None:
        if not value:
            raise ValueError('Limite de conexões não pode ser vazio.')

        if value < 1:
            raise ValueError('Limite de conexões deve ser maior que 0.')


class ExpirationDate:
    def __init__(self, value: t.Optional[datetime.datetime] = None) -> None:
        if value:
            self.__validate(value)
        self._value: t.Optional[datetime.datetime] = value

    @property
    def value(self) -> datetime.datetime:
        while not self._value:
            date = input(color_name.YELLOW + 'Data de expiração: ' + color_name.RESET)
            try:
                self._value = self.__days_to_date(int(date))
                self.__validate(self._value)
            except ValueError as e:
                print(color_name.RED + str(e) + color_name.RESET)
                self._value = None
        return self._value

    def __days_to_date(self, days: int) -> datetime.datetime:
        try:
            return datetime.datetime.now() + datetime.timedelta(days=days)
        except Exception:
            raise ValueError('Data de expiração deve ser um número inteiro.')

    def __validate(self, value: datetime.datetime) -> None:
        if not value:
            raise ValueError('Data de expiração não pode ser vazia.')

        if value < datetime.datetime.now():
            raise ValueError('Data de expiração deve ser maior que a data atual.')


class UserInputData:
    def __init__(
        self,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        connection_limit: t.Optional[int] = None,
        expiration_date: t.Optional[datetime.datetime] = None,
        v2ray_uuid: t.Optional[str] = None,
    ) -> None:
        self._username = Username(username)
        self._password = Password(password)
        self._connection_limit = ConnectionLimit(connection_limit)
        self._expiration_date = ExpirationDate(expiration_date)
        self._v2ray_uuid = v2ray_uuid

    @property
    def username(self) -> str:
        return self._username.value

    @property
    def password(self) -> str:
        return self._password.value

    @property
    def connection_limit(self) -> int:
        return self._connection_limit.value

    @property
    def expiration_date(self) -> datetime.datetime:
        return self._expiration_date.value

    @property
    def v2ray_uuid(self) -> t.Optional[str]:
        return self._v2ray_uuid

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            'username': self.username,
            'password': self.password,
            'connection_limit': self.connection_limit,
            'expiration_date': self.expiration_date,
            'v2ray_uuid': self.v2ray_uuid,
        }


class RandomUserInputData(UserInputData):
    def __init__(self, size: int = 8) -> None:
        super().__init__(
            username=''.join(random.choice(string.ascii_letters) for _ in range(size)),
            password=''.join(random.choice(string.ascii_letters) for _ in range(size)),
            connection_limit=1,
            expiration_date=datetime.datetime.now() + datetime.timedelta(days=1),
        )
