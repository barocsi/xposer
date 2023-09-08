from pydantic import Field, ConfigDict

from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.api.base.base_routers_config_model import BaseRoutersConfigModel
from xposer.sample_app.rpc_kafka.app import AppSub


class FacadeSubModel(BaseRoutersConfigModel):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class FacadeRPC(FacadeBaseClass):
    config_prefix: str = "fac_"
    app: AppSub = None

    def constructConfigModel(self) -> FacadeSubModel:
        return FacadeSubModel.model_construct(_validate=False)

    def initializeRouters(self):
        """All routers (built-in or external) must be initialized at this step"""
        self.initializeKafkaRouter(handlerFunc=self.app.RPCHandler,
                                   start_immediately=True,
                                   produce_on_result=True)

    def initializeAppsBeforeRouters(self):
        self.app = AppSub(self.ctx)

    def start(self):
        self.ctx.logger.debug(f"Facade configuration:\n{self.config.model_dump_json(indent=4)}")
        self.ctx.logger.debug(f"Facade starting: {self.__class__.__name__}")
