from abc import ABC
from typing import Any, List

from pydantic import BaseModel

from xposer.api.base.base_fastapi_service import BaseFastApiService
from xposer.api.base.base_kafka_service import BaseKafkaService
from xposer.api.base.base_service import BaseService
from xposer.core.abstract_xpcontroller import AbstractXPController
from xposer.core.context import Context


class XPControllerBaseClass(AbstractXPController, ABC):
    name: str = "XPControllerBaseClass"

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.config = self.mergeConfigurationFromPrefix()
        self.kafka_router: BaseKafkaService | Any = None
        self.socket_router: Any = None
        self.http_router: BaseFastApiService = None
        self.xpcontroller_conf_class: BaseModel
        self.services: List[BaseService] = []

    def mergeConfigurationFromPrefix(self) -> BaseModel:
        return BaseModel.model_construct()

    async def startXPControllerServices(self):
        raise NotImplementedError

    async def asyncInit(self):
        ...

    async def tearDownXPController(self):
        raise NotImplementedError
