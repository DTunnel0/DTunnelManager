from abc import ABCMeta, abstractmethod

from typing import Any


class Presenter(metaclass=ABCMeta):
    @abstractmethod
    def present(self, data: Any) -> Any:
        raise NotImplementedError
