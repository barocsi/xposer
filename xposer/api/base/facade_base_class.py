from typing import Any

from xposer.api.base.base_fastapi_router import BaseFastApiRouter
from xposer.api.base.base_kafka_router import BaseKafkaRouter
from xposer.api.base.base_kafka_router_config_model import BaseKafkaRouterConfigModel
from xposer.core.abstract_facade import AbstractFacade
from xposer.core.configure import Configurator
from xposer.core.context import Context


class FacadeBaseClass(AbstractFacade):
    name: str = "FacadeBaseClass"
    config: BaseKafkaRouterConfigModel | Any = None
    config_prefix: str = ''
    kafka_router: BaseKafkaRouter | Any = None
    socket_router: Any = None
    http_router: BaseFastApiRouter = None

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.mergeConfigurationFromPrefix()
        self.initializeAppsBeforeRouters()
        self.initializeRouters()

    def constructConfigModel(self) -> BaseKafkaRouterConfigModel:
        return self.config.model_construct(_validate=False)

    def mergeConfigurationFromPrefix(self):
        worker_config_defaults = self.constructConfigModel()
        # Merge default parameters from global config
        worker_config_merged = Configurator.mergePrefixedAttributes(worker_config_defaults,
                                                                    self.ctx.config,
                                                                    '')
        # Merge facade specific configuration parameters
        worker_config_prefix_merged = Configurator.mergePrefixedAttributes(worker_config_merged,
                                                                           self.ctx.config,
                                                                           self.config_prefix)
        worker_config_prefix_merged.model_validate(worker_config_prefix_merged)
        self.config = worker_config_prefix_merged

    def initializeAppsBeforeRouters(self):
        raise NotImplementedError

    def initializeRouters(self):
        raise NotImplementedError

    def afterInititalization(self):
        raise NotImplementedError
