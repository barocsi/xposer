import asyncio
from abc import ABC
from types import FunctionType
from typing import Any, List

from pydantic import BaseModel

from xposer.api.base.base_fastapi_service import BaseFastApiService
from xposer.api.base.base_kafka_service import BaseKafkaService
from xposer.api.base.base_service import BaseService
from xposer.core.abstract_facade import AbstractFacade
from xposer.core.context import Context


class FacadeBaseClass(AbstractFacade, ABC):
    name: str = "FacadeBaseClass"
    config: Any = None
    config_prefix: str = 'xpfacade_'
    kafka_router: BaseKafkaService | Any = None
    socket_router: Any = None
    http_router: BaseFastApiService = None
    facade_conf_class: BaseModel
    services: List[BaseService] = []

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.config = self.mergeConfigurationFromPrefix()

    def mergeConfigurationFromPrefix(self) -> BaseModel:
        return BaseModel.model_construct()

    async def initializeApps(self):
        raise NotImplementedError

    async def startServices(self):
        raise NotImplementedError

    async def asyncInit(self):
        await self.initializeApps()

    async def tearDownFacade(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.tearDownServices())
            tg.create_task(self.tearDownApp())
        self.ctx.logger.debug(f"Teardown completed for facade")

    async def tearDownServices(self):
        self.ctx.logger.debug("Tearing down services")
        async with asyncio.TaskGroup() as tg:
            print("Both tasks have completed now.")
            for service in self.services:
                tg.create_task(service.stopService())

    async def tearDownApp(self):
        self.ctx.logger.debug("Tearing down main application")
        app = self.ctx.facade.app
        if app is not None and isinstance(app.get('tearDown', None), FunctionType):
            task = asyncio.create_task(app.tearDown())
            await task
