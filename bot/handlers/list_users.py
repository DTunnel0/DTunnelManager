from telebot import TeleBot, types

from app.infra.controllers.user.get_all import GetAllUsersController

from ..middleware.permisson import AdminPermission, AllPermission, permission_required


class ListUsersHandler:
    def __init__(self, controller: GetAllUsersController, bot: TeleBot):
        self.controller = controller
        self.bot = bot

        self.bot.register_message_handler(self.handle, commands=['list_users'])

    # @permission_required(AdminPermission())
    @permission_required(AllPermission())
    def handle(self, message: types.Message):
        users = self.controller.handle()

        markup = types.ReplyKeyboardMarkup(row_width=2)
        for user in users:
            markup.add(types.KeyboardButton(user.username))

        self.bot.send_message(message.chat.id, 'Choose a user:', reply_markup=markup)
