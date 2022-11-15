import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_base import Base

DATABASE_NAME = 'db.sqlite3'
# DATABASE_PATH = (
#     '/etc/DTunnelManager/' if os.geteuid() == 0 else os.path.expanduser('~/.config/DTunnelManager/')
# )

DATABASE_PATH = './'
DATABASE_URI = 'sqlite:///' + os.path.join(DATABASE_PATH, DATABASE_NAME)

if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)


def _create_engine(uri: str) -> create_engine:
    engine = create_engine(uri, echo=False)
    Base.metadata.create_all(engine)
    return engine


class DBConnection:
    def __init__(self, uri: str = DATABASE_URI):
        self.__uri = uri
        self.__engine = _create_engine(uri)
        self.__session = None

    @property
    def uri(self) -> str:
        return self.__uri

    @property
    def engine(self) -> create_engine:
        return self.__engine

    @property
    def session(self) -> sessionmaker:
        return self.__session

    def __enter__(self) -> 'DBConnection':
        self.__session = sessionmaker()(bind=self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()
