import typing as t

from abc import ABCMeta, abstractmethod
from telebot.types import Message, CallbackQuery

from .. import bot
from ..config.bot_config import get_admin_id
from ..dealer import DealerRepository, DealerUseCase


class Permission(metaclass=ABCMeta):
    def __init__(self, user_id: int = None):
        self.user_id = user_id

    @abstractmethod
    def is_granted(self) -> bool:
        raise NotImplementedError()


class AdminPermission(Permission):
    def is_granted(self) -> bool:
        return self.user_id == get_admin_id()


class DealerPermission(Permission):
    def is_granted(self) -> bool:
        use_case = DealerUseCase(DealerRepository())
        dealer = use_case.get_by_id(self.user_id)

        if not dealer:
            return False

        return dealer.active


def permission_required(permission: t.Union[Permission, t.List[Permission]]):
    def decorator(func):
        def wrapper(message: t.Union[Message, CallbackQuery]):
            if isinstance(permission, list):
                for p in permission:
                    p.user_id = message.from_user.id

                    if p.is_granted():
                        return func(message)
            else:
                permission.user_id = message.from_user.id
                if permission.is_granted():
                    return func(message)

            try:
                bot.reply_to(message, '❌ Você não tem permissão para executar este comando')
            except Exception:
                bot.send_message(
                    chat_id=message.chat.id
                    if isinstance(message, Message)
                    else message.message.chat.id,
                    text='❌ Você não tem permissão para executar este comando',
                )

        return wrapper

    return decorator


__all__ = ['permission_required', 'AdminPermission']
