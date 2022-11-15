from telebot import types

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase

from .. import bot
from ..middleware import AdminPermission, DealerPermission, permission_required

from .helpers.dealer import (
    find_dealer_by_id,
    is_dealer,
    get_all_users_of_dealer,
    get_available_limit_creation_accounts,
)


def callback_query_menu(user_id: int = None) -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton('CRIAR USUARIO', callback_data='create_user')],
        [types.InlineKeyboardButton('DELETAR USUARIO', callback_data='delete_user')],
        [types.InlineKeyboardButton('OBTER USUARIO', callback_data='get_user')],
        [types.InlineKeyboardButton('OBTER TODOS OS USUARIOS', callback_data='list_users')],
        [types.InlineKeyboardButton('MONITOR', callback_data='monitor')],
    ]

    if not user_id or not is_dealer(user_id):
        buttons.append([types.InlineKeyboardButton('REVENDA', callback_data='revenue')])

    return types.InlineKeyboardMarkup(buttons)


def callback_query_back_menu(message: str = '🔙MENU') -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(message, callback_data='back_menu')],
    ]

    return types.InlineKeyboardMarkup(buttons)


def callback_query_back(callback_data, message: str = '🔙VOLTAR') -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(message, callback_data=callback_data)


def create_message_menu(user_id: int = None) -> str:
    text = '<b>🤖OLÁ, BEM VINDO AO BOT🤖</b>\n'

    if is_dealer(user_id):
        text += '<b>VOCÊ É UM REVENDEDOR</b>\n\n'
        text += '<b>LIMITE DE CRIAÇÃO DE CONTA:</b> <code>{}</code>\n'.format(
            find_dealer_by_id(user_id).account_creation_limit
        )
        text += '<b>LIMITE DISPONIVEL:</b> <code>{}</code>\n'.format(
            get_available_limit_creation_accounts(user_id)
        )
        text += '<b>SEU ACESSO EXPIRA EM:</b> <code>{}</code>\n'.format(
            find_dealer_by_id(user_id).expires_at
        )
        text += '<b>TOTAL CONTAS CRIADAS:</b> <code>{}</code>\n'.format(
            len(get_all_users_of_dealer(user_id, UserUseCase(UserRepository())))
        )
        text += '\n'
    else:
        text += '<b>VOCÊ É UM ADMINISTRADOR</b>\n'
        text += '\n'

    text += '<b>🖥COMANDOS DISPONIVEIS🖥</b>'

    return text


@bot.message_handler(commands=['help', 'start', 'menu'])
@permission_required([AdminPermission(), DealerPermission()])
def send_help(message: types.Message):
    bot.reply_to(
        message,
        create_message_menu(message.from_user.id),
        parse_mode='HTML',
        reply_markup=callback_query_menu(message.from_user.id),
    )


@bot.callback_query_handler(func=lambda call: call.data == 'back_menu')
@permission_required([AdminPermission(), DealerPermission()])
def back_menu(call: types.CallbackQuery):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=create_message_menu(call.from_user.id),
        reply_markup=callback_query_menu(call.from_user.id),
    )


@bot.message_handler(commands=['id'])
def send_id(message: types.Message):
    bot.reply_to(
        message=message,
        text='<b>🆔ID:</b> <code>{}</code>'.format(message.from_user.id),
        parse_mode='HTML',
    )
