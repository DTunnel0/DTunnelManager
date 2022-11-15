from telebot import types

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase

from .. import bot
from ..utilities.utils import callback_query_back_menu
from ..middleware import AdminPermission, DealerPermission, permission_required
from .message_helper import send_message_users_not_found

from .helpers.dealer import get_all_users_of_dealer, is_dealer


@bot.callback_query_handler(func=lambda query: query.data == 'list_users')
@permission_required([AdminPermission(), DealerPermission()])
def callback_query_list_users(query: types.CallbackQuery):
    user_id = query.from_user.id

    user_use_case = UserUseCase(UserRepository())
    users = (
        user_use_case.get_all()
        if not is_dealer(user_id)
        else get_all_users_of_dealer(user_id, user_use_case)
    )

    if not users:
        send_message_users_not_found(query.message, query.message.message_id)
        return

    message_reply = '<b>📝Lista de usuarios📝</b>\n\n'
    for user in users:
        message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user.username)
        message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user.password)
        message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
            user.connection_limit
        )
        message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
            user.expiration_date.strftime('%d/%m/%Y')
        )
        message_reply += '\n'

    try:
        bot.edit_message_text(
            message_reply,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )

    except Exception as e:
        import os

        filename = os.urandom(16).hex() + '.txt'
        with open(filename, 'w') as f:
            f.write(message_reply)
            f.flush()

        bot.send_document(
            query.message.chat.id,
            open(filename, 'rb'),
            reply_markup=callback_query_back_menu(),
        )
        os.remove(filename)


@bot.message_handler(regexp='/list_users')
@permission_required([AdminPermission(), DealerPermission()])
def list_users(message: types.Message):
    user_id = message.from_user.id

    user_use_case = UserUseCase(UserRepository())
    users = (
        user_use_case.get_all()
        if not is_dealer(user_id)
        else get_all_users_of_dealer(user_id, user_use_case)
    )

    if not users:
        send_message_users_not_found(message, reply_message_id=message.message_id)
        return

    message_reply = '<b>📝Lista de usuarios📝</b>\n\n'
    for user in users:
        message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user.username)
        message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user.password)
        message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
            user.connection_limit
        )
        message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
            user.expiration_date.strftime('%d/%m/%Y')
        )
        message_reply += '\n'

    try:
        bot.reply_to(
            message,
            message_reply,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
    except Exception as e:
        import os

        filename = os.urandom(16).hex() + '.txt'
        with open(filename, 'w') as f:
            f.write(message_reply)
            f.flush()

        bot.send_document(
            message.chat.id,
            open(filename, 'rb'),
            reply_markup=callback_query_back_menu(),
        )
        os.remove(filename)
