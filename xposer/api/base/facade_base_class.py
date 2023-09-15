from typing import Any, List

from pydantic import BaseModel

from xposer.api.base.base_fastapi_router import BaseFastApiRouter
from xposer.api.base.base_kafka_router import BaseKafkaRouter
from xposer.api.base.base_router import BaseRouter
from xposer.core.abstract_facade import AbstractFacade
from xposer.core.context import Context


class FacadeBaseClass(AbstractFacade):
    name: str = "FacadeBaseClass"
    config: Any = None
    config_prefix: str = 'xp_facade_'
    kafka_router: BaseKafkaRouter | Any = None
    socket_router: Any = None
    http_router: BaseFastApiRouter = None
    facade_conf_class: BaseModel
    routers: List[BaseRouter] = []


    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.config = self.mergeConfigurationFromPrefix()
        self.initializeAppsBeforeRouters()
        self.initializeRouters()

    def mergeConfigurationFromPrefix(self) -> BaseModel:
        return BaseModel.model_construct()

    def initializeAppsBeforeRouters(self):
        raise NotImplementedError

    def initializeRouters(self):
        raise NotImplementedError

    def tearDownRouters(self):
        for router in self.routers:
            router.stop_router()

    def afterInititalization(self):
        raise NotImplementedError

    def tearDown(self):
        self.tearDownRouters()
