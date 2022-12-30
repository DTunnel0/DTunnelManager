from telebot import TeleBot, types

from app.domain.use_cases.user.get_user import GetAllUsersUseCase

from ..middleware.permisson import AdminPermission, AllPermission, permission_required


class ListUsersHandler:
    def __init__(self, get_all_users: GetAllUsersUseCase, bot: TeleBot):
        self.get_all_users = get_all_users
        self.bot = bot

        self.bot.register_message_handler(self.handle, commands=['list_users'])

    @permission_required(AllPermission())
    def handle(self, message: types.Message):
        users = self.get_all_users.execute()

        markup = types.ReplyKeyboardMarkup(row_width=2)
        for user in users:
            markup.add(types.KeyboardButton(user.username))

        self.bot.send_message(message.chat.id, 'Choose a user:', reply_markup=markup)
