from telebot import types

from app.data.repositories import UserRepository
from app.domain.dtos.user import UserDto
from app.domain.use_cases import UserUseCase
from app.utilities.utils import count_connections

from .. import bot
from ..utilities.utils import callback_query_back, callback_query_back_menu
from ..middleware import AdminPermission, DealerPermission, permission_required
from .message_helper import send_message_user_not_found, send_message_users_not_found

from .helpers.dealer import find_account_by_id, get_all_users_of_dealer, is_dealer


def create_message_details(user_dto: UserDto) -> str:
    message_reply = '<b>👤Nome:</b> <code>{}</code>\n'.format(user_dto.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_dto.password)
    message_reply += '<b>📝Conexões até agora:</b> <code>{}</code>\n'.format(
        count_connections(user_dto.username)
    )
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_dto.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
        user_dto.expiration_date.strftime('%d/%m/%Y')
    )

    return message_reply


@bot.callback_query_handler(func=lambda query: query.data == 'get_user')
@permission_required([AdminPermission(), DealerPermission()])
def callback_query_get_user(query: types.CallbackQuery):
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

    buttons = []

    for i in range(0, len(users), 2):
        if i + 1 >= len(users):
            buttons.append(
                [
                    types.InlineKeyboardButton(
                        users[i].username, callback_data='get_user_' + users[i].username
                    )
                ]
            )
            continue

        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=users[i].username,
                    callback_data='get_user_' + users[i].username,
                ),
                types.InlineKeyboardButton(
                    text=users[i + 1].username,
                    callback_data='get_user_' + users[i + 1].username,
                ),
            ]
        )

    buttons.extend(callback_query_back_menu().keyboard)

    reply_markup = types.InlineKeyboardMarkup(buttons)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text='<b>📝Selecione um usuario📝</b>',
        reply_markup=reply_markup,
        parse_mode='HTML',
    )


@bot.callback_query_handler(func=lambda query: query.data.startswith('get_user_'))
@permission_required([AdminPermission(), DealerPermission()])
def callback_query_get_user(query: types.CallbackQuery):
    username = query.data.split('_')[-1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        send_message_user_not_found(query.message, query.message.message_id)
        return

    buttons = callback_query_back_menu().keyboard
    buttons[0].append(callback_query_back('get_user'))

    reply_markup = types.InlineKeyboardMarkup(buttons)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=create_message_details(user_dto),
        reply_markup=reply_markup,
        parse_mode='HTML',
    )


@bot.message_handler(regexp='/get_user (\w+)')
@permission_required([AdminPermission(), DealerPermission()])
def get_user(message: types.Message):
    username = message.text.split(' ')[1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    user_id = message.from_user.id

    if not find_account_by_id(dealer_id=user_id, account_id=user_dto.id):
        send_message_user_not_found(message, reply_message_id=message.message_id)
        return

    bot.reply_to(
        message,
        create_message_details(user_dto),
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )
