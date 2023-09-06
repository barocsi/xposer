from pydantic import Field, ConfigDict

from xposer.models.base_routers_config_model import BaseRoutersConfigModel
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.sample_app.sub.app import AppSub


class FacadeSubModel(BaseRoutersConfigModel):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class FacadeSub(FacadeBaseClass):
    name: str = "FacadeSample"
    config_prefix: str = "fac_"
    app: AppSub = None

    def constructConfigModel(self) -> FacadeSubModel:
        return FacadeSubModel.model_construct(_validate=False)

    def initializeRouters(self):
        """All routers (built-in or external) must be initialized at this step"""
        self.initializeKafkaRouter(handlerFunc=self.app.SampleCall,
                                   start_immediately=True)

    def initializeAppsBeforeRouters(self):
        self.app = AppSub(self.ctx)

    def start(self):
        self.ctx.logger.debug(f"Facade configuration:\n{self.config.model_dump_json(indent=4)}")
        self.ctx.logger.debug(f"Facade starting: {self.name}")
