from telebot import types
from datetime import datetime, timedelta

from .. import bot

from ..dealer import DealerRepository, DealerUseCase, DealerDTO
from ..dealer import AccountRepository, AccountUseCase, AccountDTO

from ..utilities.utils import callback_query_back
from ..middleware import permission_required, AdminPermission

from ..config.bot_config import get_admin_id


@bot.callback_query_handler(func=lambda call: call.data == 'revenue')
@permission_required(AdminPermission())
def revenue(call: types.CallbackQuery):
    reply_markup = types.InlineKeyboardMarkup()
    reply_markup.add(types.InlineKeyboardButton('CRIAR REVENDA', callback_data='create_revenue'))
    reply_markup.add(types.InlineKeyboardButton('EDITAR REVENDA', callback_data='edit_revenue'))
    reply_markup.add(types.InlineKeyboardButton('DELETAR REVENDA', callback_data='delete_revenue'))
    reply_markup.add(types.InlineKeyboardButton('OBTER REVENDA', callback_data='get_revenue'))
    reply_markup.add(
        types.InlineKeyboardButton('OBTER TODAS AS REVENDAS', callback_data='list_revenues')
    )
    reply_markup.add(callback_query_back('back_menu'))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>🖥COMANDOS DISPONIVEIS🖥</b>',
        reply_markup=reply_markup,
    )


@bot.callback_query_handler(func=lambda call: call.data == 'create_revenue')
@permission_required(AdminPermission())
def create_revenue(call: types.CallbackQuery):
    text = '<b>Ex: </b>@user | 1000000\n'
    text += '<b>👤Nome de usuário ou ID:</b>'

    message = bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, process_create_revenue)


def process_create_revenue(message: types.Message):
    username = message.text

    if not username:
        bot.reply_to(
            message=message,
            text='<b>❌Nome de usuário não informado❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    try:
        profile = bot.get_chat(username)
    except:
        profile = None

    if not profile:
        bot.reply_to(
            message=message,
            text='<b>❌Nome de usuário inválido❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    use_case = DealerUseCase(DealerRepository())
    if use_case.get_by_id(profile.id):
        bot.reply_to(
            message=message,
            text='<b>❌Usuário já existe❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    if profile.id == get_admin_id():
        bot.reply_to(
            message=message,
            text='<b>❌Você e o administrador não podem ser revendedor❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(username)
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(profile.id)
    text += '<b>👤Nome:</b> <code>{}</code>\n'.format(profile.first_name)
    text += '<b>👤Sobrenome:</b> <code>{}</code>\n'.format(profile.last_name)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n\n'.format(profile.username)
    text += '<b>🚫Limite de criação de contas:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, process_create_revenue_limit, profile=profile)


def process_create_revenue_limit(message: types.Message, profile: types.User):
    limit = message.text

    if not limit:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Limite não informado❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    try:
        limit = int(limit)
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Limite inválido❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(profile.username)
    text += '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n\n'.format(limit)
    text += '<b>📆Data de expiração (Em dias):</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(
        message, process_create_revenue_expiration, profile=profile, limit=limit
    )


def process_create_revenue_expiration(message: types.Message, profile: types.User, limit: int):
    expiration = message.text

    if not expiration:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Data de expiração não informada❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    try:
        expiration = int(expiration)
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Data de expiração inválida❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    dealer = DealerDTO()
    dealer.id = profile.id
    dealer.name = (profile.first_name + ' ' + (profile.last_name or '')).strip()
    dealer.username = profile.username
    dealer.account_creation_limit = limit
    dealer.expires_at = expiration

    use_case = DealerUseCase(DealerRepository())

    try:
        dealer = use_case.create(dealer)
    except Exception as e:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Erro ao criar conta❌</b>\n<code>{}</code>'.format(e),
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>✅CONTA CRIADA COM SUCESSO✅</b>\n\n'
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome:</b> <code>{}</code>\n'.format(dealer.name)
    text += '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n'.format(
        dealer.account_creation_limit
    )
    text += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(dealer.expires_at)

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )


@bot.callback_query_handler(func=lambda call: call.data == 'edit_revenue')
@permission_required(AdminPermission())
def edit_revenue(call: types.CallbackQuery):
    text = '<b>👤Nome de usuário ou ID:</b>'

    message = bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, process_edit_revenue)


def process_edit_revenue(message: types.Message):
    username = message.text

    if not username:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Nome de usuário não informado❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    username = username.replace('@', '')

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_username(username) or use_case.get_by_id(username)

    account_use_case = AccountUseCase(AccountRepository())

    if not dealer:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Conta não encontrada❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)
    text += '<b>💰Total de contas criadas:</b> <code>{}</code>\n'.format(
        len(account_use_case.get_all_by_dealer_id(dealer.id))
    )
    text += '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n'.format(
        dealer.account_creation_limit
    )
    text += '<b>🔘Status:</b> <code>{}</code>\n'.format('Ativo' if dealer.active else 'Inativo')
    text += '<b>📆Data de expiração:</b> <code>{}</code>\n\n'.format(dealer.expires_at)

    reply_markup = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    text='EDITAR LIMITE DE CRIAÇÃO DE CONTAS',
                    callback_data='edit_revenue_limit_{}'.format(dealer.id),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text='EDITAR DATA DE EXPIRAÇÃO',
                    callback_data='edit_revenue_expiration_{}'.format(dealer.id),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text='DESATIVAR CONTA',
                    callback_data='disable_revenue_{}'.format(dealer.id),
                )
                if dealer.active
                else types.InlineKeyboardButton(
                    text='ATIVAR CONTA',
                    callback_data='enable_revenue_{}'.format(dealer.id),
                ),
            ],
            [callback_query_back('revenue')],
        ]
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=reply_markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_revenue_limit_'))
@permission_required(AdminPermission())
def edit_revenue_limit(call: types.CallbackQuery):
    dealer_id = call.data.split('_')[-1]

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)

    if not dealer:
        bot.send_message(
            chat_id=call.message.chat.id,
            text='<b>❌Conta não encontrada❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n'.format(
        dealer.account_creation_limit
    )

    message = bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, process_edit_revenue_limit, dealer_id)


def process_edit_revenue_limit(message: types.Message, dealer_id: str):
    limit = message.text

    if not limit:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Limite não informado❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    try:
        limit = int(limit)
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Limite inválido❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)
    dealer.account_creation_limit = limit

    try:
        dealer = use_case.update(dealer)
    except Exception as e:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Erro ao atualizar conta❌</b>\n<code>{}</code>'.format(e),
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>✅CONTA ATUALIZADA COM SUCESSO✅</b>\n\n'
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)
    text += '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n'.format(
        dealer.account_creation_limit
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_revenue_expiration_'))
@permission_required(AdminPermission())
def edit_revenue_expiration(call: types.CallbackQuery):
    dealer_id = call.data.split('_')[-1]

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)

    if not dealer:
        bot.send_message(
            chat_id=call.message.chat.id,
            text='<b>❌Conta não encontrada❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>📆Data de expiração em dias📆</b>\n'
    text += '<b>Ex:</b> <code>30</code>\n\n'
    text += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(dealer.expires_at)

    message = bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, process_edit_revenue_expiration, dealer_id)


def process_edit_revenue_expiration(message: types.Message, dealer_id: str):
    expiration = message.text

    if not expiration:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Data de expiração não informada❌</b>',
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)
    dealer.expires_at = (datetime.now() + timedelta(days=int(expiration))).strftime('%d/%m/%Y')

    try:
        dealer = use_case.update(dealer)
    except Exception as e:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌Erro ao atualizar conta❌</b>\n<code>{}</code>'.format(e),
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>✅CONTA ATUALIZADA COM SUCESSO✅</b>\n\n'
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)
    text += '<b>🚫Data de expiração:</b> <code>{}</code>\n'.format(dealer.expires_at)

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('disable_revenue_'))
@permission_required(AdminPermission())
def disable_revenue(call: types.CallbackQuery):
    dealer_id = call.data.split('_')[-1]

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)
    dealer.active = False

    try:
        dealer = use_case.update(dealer)
    except Exception as e:
        bot.send_message(
            chat_id=call.message.chat.id,
            text='<b>❌Erro ao atualizar conta❌</b>\n<code>{}</code>'.format(e),
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>✅CONTA DESATIVADA COM SUCESSO✅</b>\n\n'
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)

    bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('enable_revenue_'))
@permission_required(AdminPermission())
def enable_revenue(call: types.CallbackQuery):
    dealer_id = call.data.split('_')[-1]

    use_case = DealerUseCase(DealerRepository())
    dealer = use_case.get_by_id(dealer_id)
    dealer.active = True

    try:
        dealer = use_case.update(dealer)
    except Exception as e:
        bot.send_message(
            chat_id=call.message.chat.id,
            text='<b>❌Erro ao atualizar conta❌</b>\n<code>{}</code>'.format(e),
            reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
        )
        return

    text = '<b>✅CONTA ATIVADA COM SUCESSO✅</b>\n\n'
    text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
    text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)

    bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )


@bot.callback_query_handler(func=lambda call: call.data == 'list_revenues')
@permission_required(AdminPermission())
def revenue_list(call: types.CallbackQuery):
    use_case = DealerUseCase(DealerRepository())
    dealers = use_case.get_all()

    account_use_case = AccountUseCase(AccountRepository())

    text = '<b>📝Lista de contas📝</b>\n\n'
    for dealer in dealers:
        text += '<b>👤Nome de usuário:</b> <code>{}</code>\n'.format(dealer.username)
        text += '<b>👤ID:</b> <code>{}</code>\n'.format(dealer.id)
        text += '<b>👤Nome:</b> <code>{}</code>\n'.format(dealer.name)
        text += '<b>💰Total de contas criadas:</b> <code>{}</code>\n'.format(
            len(account_use_case.get_all_by_dealer_id(dealer.id))
        )
        text += '<b>🚫Limite de criação de contas:</b> <code>{}</code>\n'.format(
            dealer.account_creation_limit
        )
        text += '<b>🔘Status:</b> <code>{}</code>\n'.format('Ativo' if dealer.active else 'Inativo')
        text += '<b>📆Data de expiração:</b> <code>{}</code>\n\n'.format(dealer.expires_at)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup([[callback_query_back('revenue')]]),
    )
