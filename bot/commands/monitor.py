from telebot import types

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase
from app.utilities.utils import count_connections

from .. import bot
from ..utilities.utils import callback_query_back_menu
from ..middleware import AdminPermission, DealerPermission, permission_required

from .helpers.dealer import get_all_users_of_dealer, is_dealer


@bot.message_handler(regexp='/monitor')
@permission_required([AdminPermission(), DealerPermission()])
def monitor(message: types.Message):
    user_use_case = UserUseCase(UserRepository())
    users = (
        user_use_case.get_all()
        if not is_dealer(message.from_user.id)
        else get_all_users_of_dealer(message.from_user.id, user_use_case)
    )

    if not users:
        bot.reply_to(message, '❌ <b>Nao foi possivel encontrar usuarios</b>')
        return

    message_reply = '<b>MOME | CONEXOES | LIMITE | DATA DE EXPIRACAO</b>\n\n'
    width_user = max(len(user.username) for user in users)
    width_limit = max(len(str(user.connection_limit)) for user in users)

    for user in users:
        message_reply += '<code>'
        message_reply += '{} | '.format(user.username.ljust(width_user))
        message_reply += '{} | '.format(('%02d' % count_connections(user.username)).ljust(2))
        message_reply += '{} | '.format(('%02d' % user.connection_limit).ljust(width_limit))
        message_reply += '{}'.format(user.expiration_date.strftime('%d/%m/%Y'))
        message_reply += '</code>\n'

    bot.reply_to(
        message,
        message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'monitor')
@permission_required([AdminPermission(), DealerPermission()])
def callback_query__monitor(query: types.CallbackQuery):
    user_use_case = UserUseCase(UserRepository())
    users = (
        user_use_case.get_all()
        if not is_dealer(query.from_user.id)
        else get_all_users_of_dealer(query.from_user.id, user_use_case)
    )

    if not users:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text='❌ <b>Nao foi possivel encontrar usuarios</b>',
            reply_markup=callback_query_back_menu(),
            parse_mode='HTML',
        )
        return

    message_reply = '<b>MOME | LIMITE | CONEXOES | DATA DE EXPIRACAO</b>\n\n'
    width_user = max(len(user.username) for user in users)
    width_limit = max(len(str(user.connection_limit)) for user in users)

    for user in users:
        message_reply += '<code>'
        message_reply += '{} | '.format(user.username.ljust(width_user))
        message_reply += '{} | '.format(('%02d' % user.connection_limit).ljust(width_limit))
        message_reply += '{} | '.format(('%02d' % count_connections(user.username)).ljust(2))
        message_reply += '{}'.format(user.expiration_date.strftime('%d/%m/%Y'))
        message_reply += '</code>\n'

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )
