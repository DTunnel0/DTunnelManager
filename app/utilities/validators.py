from datetime import datetime, timedelta
from .logger import logger
from .utils import find_user_by_name


class UserValidator:
    def __init__(self, user_dto):
        self.user_dto = user_dto

    @staticmethod
    def validate_username(username) -> bool:
        if not username:
            logger.error('Nome de usuário não informado')
            return False

        if len(username) < 3:
            logger.error('Nome de usuário deve conter no mínimo 3 caracteres')
            return False

        if len(username) > 20:
            logger.error('Nome de usuário deve conter no máximo 20 caracteres')
            return False

        if not username.isalnum():
            logger.error('Nome de usuário deve conter apenas letras e números')
            return False

        if find_user_by_name(username):
            logger.error('Nome de usuário já existe')
            return False

        return True

    @staticmethod
    def validate_password(password) -> bool:
        if not password:
            logger.error('Senha não informada')
            return False

        if len(password) < 3:
            logger.error('Senha deve conter no mínimo 3 caracteres')
            return False

        if len(password) > 20:
            logger.error('Senha deve conter no máximo 20 caracteres')
            return False

        if not password.isalnum():
            logger.error('Senha deve conter apenas letras e números')
            return False

        return True

    @staticmethod
    def validate_connection_limit(limit: int) -> bool:
        if not limit:
            logger.error('Limite de conexões não informado')
            return False

        if isinstance(limit, str) and not limit.isdigit():
            logger.error('Limite de conexões deve conter apenas números')
            return False

        if int(limit) < 1:
            logger.error('Limite de conexões deve ser maior que 0')
            return False

        return True

    @staticmethod
    def validate_expiration_date(date: str) -> bool:
        if not date:
            logger.error('Data de expiração não informada')
            return False

        if isinstance(date, str) and date.isdigit() and int(date) > 1:
            date = datetime.now() + timedelta(days=int(date))  # type: ignore

        try:
            if not isinstance(date, datetime):
                datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            logger.error('Data de expiração inválida')
            return False

        return True

    @staticmethod
    def validate(user_dto) -> bool:
        return (
            UserValidator.validate_username(user_dto.username)
            and UserValidator.validate_password(user_dto.password)
            and UserValidator.validate_connection_limit(user_dto.connection_limit)
            and UserValidator.validate_expiration_date(user_dto.expiration_date)
        )


validate_user = UserValidator.validate
validate_username = UserValidator.validate_username
validate_password = UserValidator.validate_password
validate_connection_limit = UserValidator.validate_connection_limit
validate_expiration_date = UserValidator.validate_expiration_date
