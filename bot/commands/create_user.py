import datetime

from telebot import types

from app.data.gateway.user import SystemUserGateway
from app.data.repositories import UserRepository
from app.domain.dtos import UserDto
from app.domain.use_cases.user.create_user import CreateUserUseCase, UserInputDTO
from app.utilities.validators import UserValidator

from .. import bot
from ..middleware import AdminPermission, DealerPermission, permission_required
from ..utilities.utils import callback_query_back_menu
from .helpers.dealer import decrement_account_creation_limit, has_limit_available, is_dealer


def send_message_user_created(message: types.Message, user_created: UserInputDTO):
    message_reply = '<b>✅USUARIO CRIADO COM SUCESSO✅</b>\n\n'
    message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user_created.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_created.password)
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_created.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
        user_created.expiration_date.strftime('%d/%m/%Y')
    )

    bot.reply_to(
        message=message,
        text=message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'create_user')
@permission_required([AdminPermission(), DealerPermission()])
def callback_query_create_user(query: types.CallbackQuery):
    user_id = query.from_user.id
    if is_dealer(user_id) and not has_limit_available(user_id):
        bot.answer_callback_query(
            callback_query_id=query.id,
            text='❌ Você atingiu o limite de criação de usuários',
            show_alert=True,
        )
        return

    message = bot.send_message(
        chat_id=query.message.chat.id,
        text='<b>👤Nome do usuario:</b>',
        parse_mode='HTML',
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, proccess_username)


def proccess_username(message: types.Message):
    username = message.text

    if not UserValidator.validate_username(username):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ NOME DE USUARIO INVALIDO',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=types.ForceReply(selective=True),
    )
    bot.register_next_step_handler(message, proccess_password, username=username)


def proccess_password(message: types.Message, username: str):
    password = message.text

    if not UserValidator.validate_password(password):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ SENHA INVALIDA',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b> <code>{}</code>\n'.format(password)
    reply_text += '<b>🚫Limite de conexões:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(
        message,
        proccess_limit_connections,
        username=username,
        password=password,
    )


def proccess_limit_connections(message: types.Message, username: str, password: str):
    limit = message.text

    if not UserValidator.validate_connection_limit(limit):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ LIMITE DE CONEXOES INVALIDO',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b> <code>{}</code>\n'.format(password)
    reply_text += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(limit)
    reply_text += '<b>📆Data de expiração:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(
        message,
        proccess_expiration_date,
        username=username,
        password=password,
        limit=limit,
    )


def proccess_expiration_date(message: types.Message, username: str, password: str, limit: str):
    expiration = message.text

    if not UserValidator.validate_expiration_date(expiration):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ DATA DE EXPIRACAO INVALIDA',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    repository = UserRepository()
    gateway = SystemUserGateway()
    create_user_use_case = CreateUserUseCase(repository, gateway)
    data = UserInputDTO(
        username=username,
        password=password,
        connection_limit=int(limit),
        expiration_date=expiration,
    )
    create_user_use_case.execute(data)
    send_message_user_created(message, data)
    decrement_account_creation_limit(message.chat.id, gateway.get_user_id(data.username))


@bot.message_handler(regexp=r'/create_user (\w+) (\w+) (\d+) (\d+)')
@permission_required([AdminPermission(), DealerPermission()])
def create_user(message: types.Message):
    user_id = message.from_user.id
    if is_dealer(user_id) and not has_limit_available(user_id):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ Você atingiu o limite de criação de usuários',
        )
        return

    username = message.text.split(' ')[1]
    password = message.text.split(' ')[2]

    limit_connections = message.text.split(' ')[3]
    expiration_date = message.text.split(' ')[4]

    if not limit_connections.isdigit():
        bot.reply_to(
            message,
            '❌ Limite de conexões deve ser um número',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    if not expiration_date.isdigit():
        bot.reply_to(
            message,
            '❌ Data de expiração deve ser um número',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    limit_connections = int(limit_connections)
    expiration_date = int(expiration_date)

    if limit_connections < 1:
        bot.reply_to(
            message,
            '❌ Limite de conexões deve ser maior que 0',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    if expiration_date < 1:
        bot.reply_to(
            message,
            '❌ Data de expiração deve ser maior que 0',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    # user_use_case = UserUseCase(UserRepository())
    repository = UserRepository()
    gateway = SystemUserGateway()
    create_user_use_case = CreateUserUseCase(repository, gateway)
    data = UserInputDTO(
        username=username,
        password=password,
        v2ray_uuid=None,
        connection_limit=limit_connections,
        expiration_date=datetime.datetime.now() + datetime.timedelta(days=expiration_date),
    )
    user_dto = UserDto.of(
        {
            'username': username,
            'password': password,
            'connection_limit': limit_connections,
            'expiration_date': datetime.datetime.now() + datetime.timedelta(days=expiration_date),
        }
    )

    if not UserValidator.validate(user_dto):
        bot.reply_to(
            message,
            '❌ <b>Nao foi possivel criar o usuario</b>',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    try:
        create_user_use_case.execute(data)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    send_message_user_created(message, data)
    decrement_account_creation_limit(user_id, gateway.get_user_id(username))
