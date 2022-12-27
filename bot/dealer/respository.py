from typing import List

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func

DB_URI = 'sqlite:///db.sqlite3'
BASE = declarative_base()


class DBConnection:
    def __init__(self, uri: str = DB_URI):
        self.__uri = uri
        self.__engine = create_engine(self.__uri)
        self.__session = None

        BASE.metadata.create_all(self.__engine)

    @property
    def uri(self) -> str:
        return self.__uri

    @property
    def engine(self):
        return self.__engine

    @property
    def session(self) -> sessionmaker:
        return self.__session

    def __enter__(self) -> 'DBConnection':
        self.__session = sessionmaker()(bind=self.engine)
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()


class Model(BASE):
    __abstract__ = True

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Dealer(Model):
    __tablename__ = 'dealers'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    username = Column(String, nullable=False)

    account_creation_limit = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime, nullable=False, default=func.now())
    active = Column(Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'account_creation_limit': self.account_creation_limit,
            'expires_at': self.expires_at.strftime('%d/%m/%Y'),
            'active': self.active,
        }


class Account(Model):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    dealer_id = Column(Integer, ForeignKey('dealers.id'), nullable=False)


class DealerRepository:
    def create(
        self,
        id: int,
        name: str,
        username: str,
        account_creation_limit: int,
        expires_at: str,
    ) -> Dealer:
        with DBConnection() as session:
            dealer = Dealer(
                id=id,
                name=name,
                username=username,
                account_creation_limit=account_creation_limit,
                expires_at=expires_at,
            )
            session.add(dealer)
            session.commit()
            session.refresh(dealer)

        return dealer

    def get_by_id(self, id: int) -> Dealer:
        with DBConnection() as session:
            return session.query(Dealer).filter(Dealer.id == id).first()

    def get_by_username(self, username: str) -> Dealer:
        with DBConnection() as session:
            return session.query(Dealer).filter(Dealer.username == username).first()

    def get_all(self) -> list:
        with DBConnection() as session:
            return session.query(Dealer).all()

    def update(self, dealer: Dealer) -> Dealer:
        with DBConnection() as session:
            session.merge(dealer)
            session.commit()

            return dealer

    def delete(self, dealer: Dealer) -> Dealer:
        with DBConnection() as session:
            session.delete(dealer)
            session.commit()

            return dealer


class AccountRepository:
    def create(self, account_id: int, dealer_id: int) -> Account:
        with DBConnection() as session:
            account = Account(
                id=account_id,
                dealer_id=dealer_id,
            )
            session.add(account)
            session.commit()
            session.refresh(account)

        return account

    def get_by_id(self, dealer_id: int, id: int) -> Account:
        with DBConnection() as session:
            return (
                session.query(Account)
                .filter(Account.id == id, Account.dealer_id == dealer_id)
                .first()
            )

    def get_by_dealer_id(self, dealer_id: int) -> List[Account]:
        with DBConnection() as session:
            return session.query(Account).filter(Account.dealer_id == dealer_id).all()

    def get_all(self) -> list:
        with DBConnection() as session:
            return session.query(Account).all()

    def update(self, account: Account) -> Account:
        with DBConnection() as session:
            session.merge(account)
            session.commit()

            return account

    def delete(self, account: Account) -> Account:
        with DBConnection() as session:
            session.delete(account)
            session.commit()

            return account
