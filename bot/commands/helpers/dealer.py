import typing as t

from app.domain.use_cases import UserUseCase

from bot.dealer import DealerRepository, AccountRepository
from bot.dealer import DealerUseCase, AccountUseCase
from bot.dealer import DealerDTO, AccountDTO


def is_dealer(user_id: int) -> bool:
    dealer_use_case = DealerUseCase(DealerRepository())
    return dealer_use_case.get_by_id(user_id) is not None


def has_limit_available(user_id: int) -> bool:
    dealer_use_case = DealerUseCase(DealerRepository())
    dealer_dto = dealer_use_case.get_by_id(user_id)

    if not dealer_dto:
        return False

    account_use_case = AccountUseCase(AccountRepository())
    return dealer_dto.account_creation_limit > len(account_use_case.get_all_by_dealer_id(user_id))


def get_available_limit_creation_accounts(user_id: int) -> int:
    dealer_use_case = DealerUseCase(DealerRepository())
    dealer = dealer_use_case.get_by_id(user_id)

    if not dealer:
        return 0

    account_use_case = AccountUseCase(AccountRepository())
    limit = dealer.account_creation_limit - len(account_use_case.get_all_by_dealer_id(user_id))
    return limit if limit > 0 else 0


def decrement_account_creation_limit(user_id: int, account_id: int) -> None:
    dealer_use_case = DealerUseCase(DealerRepository())
    dealer_dto = dealer_use_case.get_by_id(user_id)

    if not dealer_dto:
        return

    account_use_case = AccountUseCase(AccountRepository())
    account_use_case.create(AccountDTO(id=account_id, dealer_id=user_id))


def increment_account_creation_limit(user_id: int, account_id: int) -> None:
    dealer_use_case = DealerUseCase(DealerRepository())
    dealer = dealer_use_case.get_by_id(user_id)

    if not dealer:
        return

    account_use_case = AccountUseCase(AccountRepository())
    account_use_case.delete(user_id, account_id)


def find_account_by_id(user_id: int, account_id: int) -> t.Optional[AccountDTO]:
    account_use_case = AccountUseCase(AccountRepository())
    return account_use_case.get_by_id(user_id, account_id)


def find_dealer_by_id(user_id: int) -> t.Optional[DealerDTO]:
    dealer_use_case = DealerUseCase(DealerRepository())
    return dealer_use_case.get_by_id(user_id)


def get_all_users_of_dealer(user_id: int, user_use_case: UserUseCase) -> t.List[AccountDTO]:
    account_use_case = AccountUseCase(AccountRepository())
    accounts = account_use_case.get_all_by_dealer_id(user_id)
    return [user_use_case.get_by_id(account.id) for account in accounts]
