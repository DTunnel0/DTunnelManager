from typing import Optional, List
from datetime import datetime, timedelta

from .respository import DealerRepository, AccountRepository


class DealerDTO:
    id: int = None
    name: str = None
    username: str = None
    account_creation_limit: int = None
    expires_at: str = None
    active: bool = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'account_creation_limit': self.account_creation_limit,
            'expires_at': self.expires_at,
            'active': self.active,
        }


class AccountDTO:
    id: int = None
    dealer_id: int = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class DealerUseCase:
    def __init__(self, repository: DealerRepository):
        self.repository = repository

    def create(self, dto: DealerDTO) -> DealerDTO:
        if not dto.name:
            raise ValueError('Name is required')

        if not dto.username:
            raise ValueError('Username is required')

        if self.repository.get_by_username(dto.username):
            raise ValueError('Username already exists')

        expires_at = datetime.now() + timedelta(days=30)

        try:
            expires_at = datetime.now() + timedelta(days=int(dto.expires_at))
        except ValueError:
            try:
                expires_at = datetime.strptime(dto.expires_at, '%d/%m/%Y')
            except ValueError:
                raise ValueError('Invalid expires_at format')

        dealer = self.repository.create(
            id=dto.id,
            name=dto.name,
            username=dto.username,
            account_creation_limit=dto.account_creation_limit,
            expires_at=expires_at,
        )

        return DealerDTO(**dealer.to_dict())

    def get_by_id(self, id: int) -> Optional[DealerDTO]:
        dealer = self.repository.get_by_id(id)

        if not dealer:
            return None

        return DealerDTO(**dealer.to_dict())

    def get_by_username(self, username: str) -> Optional[DealerDTO]:
        dealer = self.repository.get_by_username(username)

        if not dealer:
            return None

        return DealerDTO(**dealer.to_dict())

    def get_all(self) -> List[DealerDTO]:
        dealers = self.repository.get_all()

        return [DealerDTO(**dealer.to_dict()) for dealer in dealers]

    def update(self, dto: DealerDTO) -> DealerDTO:
        if not dto.id:
            raise ValueError('Id is required')

        dealer = self.repository.get_by_id(dto.id)

        if not dealer:
            raise ValueError('Dealer not found')

        if dto.name:
            dealer.name = dto.name

        if dto.username:
            dealer.username = dto.username

        if dto.account_creation_limit:
            dealer.account_creation_limit = dto.account_creation_limit

        if dto.expires_at:
            try:
                dealer.expires_at = datetime.strptime(dto.expires_at, '%d/%m/%Y')
            except ValueError:
                raise ValueError('Invalid expires_at format')

        if dto.active:
            dealer.active = 1
        else:
            dealer.active = 0

        self.repository.update(dealer)

        return DealerDTO(**dealer.to_dict())

    def delete(self, id: int) -> bool:
        dealer = self.repository.get_by_id(id)

        if not dealer:
            return False

        self.repository.delete(dealer)

        return True


class AccountUseCase:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def create(self, account: AccountDTO) -> AccountDTO:
        if not account.id:
            raise ValueError('Id is required')

        if not account.dealer_id:
            raise ValueError('Dealer id is required')

        account = self.repository.create(account_id=account.id, dealer_id=account.dealer_id)

        return AccountDTO(
            id=account.id,
            dealer_id=account.dealer_id,
        )

    def get_by_id(self, dealer_id: int, account_id: int) -> Optional[AccountDTO]:
        account = self.repository.get_by_id(dealer_id, account_id)

        if not account:
            return None

        return AccountDTO(
            id=account.id,
            dealer_id=account.dealer_id,
        )

    def get_all_by_dealer_id(self, dealer_id: int) -> List[AccountDTO]:
        accounts = self.repository.get_by_dealer_id(dealer_id)
        return [
            AccountDTO(
                id=account.id,
                dealer_id=account.dealer_id,
            )
            for account in accounts
        ]

    def get_all(self) -> List[AccountDTO]:
        accounts = self.repository.get_all()
        return [
            AccountDTO(
                id=account.id,
                dealer_id=account.dealer_id,
            )
            for account in accounts
        ]

    def update(self, account: AccountDTO) -> AccountDTO:
        if not account.id:
            raise ValueError('Id is required')

        if not account.dealer_id:
            raise ValueError('Dealer id is required')

        account = self.repository.update(account)

        return AccountDTO(
            id=account.id,
            dealer_id=account.dealer_id,
        )

    def delete(self, dealer_id: int, account_id: int) -> bool:
        account = self.repository.get_by_id(dealer_id, account_id)

        if not account:
            return False

        self.repository.delete(account)

        return True
