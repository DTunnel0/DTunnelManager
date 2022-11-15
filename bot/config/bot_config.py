from .config import ConfigParser

parser = ConfigParser()

BOT_TOKEN = parser.get('bot_token')
ADMIN_ID = parser.get('admin_id')


def set_bot_token(token: str):
    if not isinstance(token, str):
        raise ValueError('Bot token must be a string')

    parser.set('bot_token', token)
    parser.save()


def set_admin_id(id: int):
    if not isinstance(id, int):
        raise ValueError('Admin ID must be an integer')

    parser.set('admin_id', id)
    parser.save()


def get_bot_token():
    return parser.get('bot_token')


def get_admin_id():
    admin_id = parser.get('admin_id')
    return int(admin_id) if admin_id else None
