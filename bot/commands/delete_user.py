from telebot import types

from app.data.repositories import UserRepository
from app.data.gateway.user import SystemUserGateway
from app.domain.use_cases.user.delete_user import DeleteUserUseCase
from app.domain.use_cases.user.get_user import GetAllUsersUseCase

from .message_helper import send_message_user_not_found, send_message_users_not_found

from .. import bot
from ..utilities.utils import callback_query_back_menu
from ..middleware import AdminPermission, DealerPermission, permission_required
from .helpers.dealer import find_account_by_id, increment_account_creation_limit, is_dealer


def send_message_deleted(message: types.Message, username: str):
    reply_text = '<b>✅USUARIO DELETADO COM SUCESSO✅</b>\n'
    reply_text += '<b>👤Nome do usuario: </b> <code>{}</code>'.format(username)

    bot.reply_to(
        message,
        reply_text,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'delete_user')
@permission_required([AdminPermission(), DealerPermission()])
def callback_query_delete_user(query: types.CallbackQuery):
    # gateway = SystemUserGateway()
    repository = UserRepository()
    # use_case = DeleteUserUseCase(repository, gateway)

    if not GetAllUsersUseCase(repository).execute():
        send_message_users_not_found(query.message)
        return

    message = bot.send_message(
        chat_id=query.message.chat.id,
        text='<b>👤Nome do usuario: </b>',
        parse_mode='HTML',
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, proccess_username_delete)


def proccess_username_delete(message: types.Message):
    username = message.text

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    user_id = message.from_user.id

    if is_dealer(user_id) and not find_account_by_id(user_id=user_id, account_id=user_dto.id):
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    user_use_case.delete(user_dto.id)

    send_message_deleted(message, username)
    increment_account_creation_limit(message.chat.id, user_dto.id)


@bot.message_handler(regexp='/delete_user (\w+)')
@permission_required([AdminPermission(), DealerPermission()])
def delete_user(message: types.Message):
    username = message.text.split(' ')[1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    user_id = message.from_user.id

    if is_dealer(user_id) and not find_account_by_id(user_id=user_id, account_id=user_dto.id):
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    try:
        user_use_case.delete(user_dto.id)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    send_message_deleted(message, username)
    increment_account_creation_limit(message.chat.id, user_dto.id)
