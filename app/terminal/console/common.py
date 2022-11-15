from abc import ABCMeta, abstractmethod

from app.utilities.logger import logger


class Callback(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> None:
        try:
            self.execute(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
