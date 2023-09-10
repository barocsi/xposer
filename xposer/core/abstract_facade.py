from abc import ABC, abstractmethod

from xposer.core.context import Context


class AbstractFacade(ABC):
    _ctx: Context

    @property
    @abstractmethod
    def name(self):
        pass

    @name.setter
    @abstractmethod
    def name(self, value):
        pass

    @property
    def ctx(self):
        return self._ctx

    @ctx.setter
    def ctx(self, value):
        self._ctx = value

    def __init__(self, ctx: Context):
        self._ctx = ctx
        pass

    @abstractmethod
    def constructConfigModel(self):
        pass

    @abstractmethod
    def afterInititalization(self):
        pass
