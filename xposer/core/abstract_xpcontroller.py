from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from xposer.core.context import Context

T = TypeVar('T')


class AbstractXPController(ABC, Generic[T]):
    xpcontroller_conf_class: Type[T]

    def __init__(self, ctx: Context):
        self._ctx = ctx

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        ...

    @property
    def ctx(self) -> Context:
        return self._ctx

    @ctx.setter
    def ctx(self, value: Context) -> None:
        self._ctx = value

    @abstractmethod
    async def startXPControllerServices(self) -> None:
        ...

    @abstractmethod
    async def tearDownXPControllerServices(self) -> None:
        ...

    @abstractmethod
    def mergeConfigurationFromPrefix(self) -> T:
        ...

    @abstractmethod
    async def tearDownXPController(self) -> None:
        ...

    @abstractmethod
    async def asyncInit(self) -> None:
        ...
