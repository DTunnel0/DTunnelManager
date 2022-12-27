from telebot import types

from bot import bot
from bot.utilities.utils import callback_query_back_menu


def send_message_user_not_found(
    message: types.Message,
    edit_message_id: int = None,
    reply_message_id: int = None,
):
    text = '<b>❌ USUARIO NAO ENCONTRADO</b>'

    if edit_message_id:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=edit_message_id,
            text=text,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    bot.send_message(
        message.chat.id,
        reply_to_message_id=reply_message_id,
        text=text,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


def send_message_users_not_found(
    message: types.Message,
    edit_message_id: int = None,
    reply_message_id: int = None,
):
    text = '<b>❌ NENHUM USUARIO ENCONTRADO</b>'

    if edit_message_id:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=edit_message_id,
            text=text,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    bot.send_message(
        message.chat.id,
        reply_to_message_id=reply_message_id,
        text=text,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )
