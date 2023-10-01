from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from xposer.core.context import Context

T = TypeVar('T')


class AbstractXPController(ABC, Generic[T]):
    _ctx: Context
    xpcontroller_conf_class: Type[T]

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
    async def startXPControllerServices(self):
        ...

    @abstractmethod
    def mergeConfigurationFromPrefix(self) -> T:
        ...

    @abstractmethod
    async def tearDownXPController(self):
        pass
