import typing as t
from abc import ABCMeta, abstractmethod

from telebot.types import CallbackQuery, Message

from .. import bot
from ..config.bot_config import get_admin_id
from ..dealer import DealerRepository, DealerUseCase


class Permission(metaclass=ABCMeta):
    @abstractmethod
    def is_granted(self, user_id: int) -> bool:
        raise NotImplementedError()


class AdminPermission(Permission):
    def is_granted(self, user_id: int) -> bool:
        return user_id == get_admin_id()


class DealerPermission(Permission):
    def is_granted(self, user_id: int) -> bool:
        use_case = DealerUseCase(DealerRepository())
        dealer = use_case.get_by_id(user_id)

        if not dealer:
            return False

        return dealer.active


class AllPermission(Permission):
    def is_granted(self, user_id: int) -> bool:
        return True


def permission_required(permission: t.Union[Permission, t.List[Permission]]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            message: t.Union[Message, CallbackQuery] = args[-1]
            if isinstance(permission, list):
                for p in permission:
                    if p.is_granted(message.from_user.id):
                        return func(*args, **kwargs)

            if permission.is_granted(message.from_user.id):
                return func(*args, **kwargs)

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
