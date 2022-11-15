from telebot import types


def callback_query_back_menu(message: str = '🔙MENU') -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(message, callback_data='back_menu')],
    ]

    return types.InlineKeyboardMarkup(buttons)


def callback_query_back(callback_data, message: str = '🔙VOLTAR') -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(message, callback_data=callback_data)
