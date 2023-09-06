from pydantic import Field
from pydantic_settings import BaseSettings
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.sample_app.sub import AppLogicSample


class FacadeSampleConfigModel(BaseSettings):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')


class FacadeSample(FacadeBaseClass):
    name: str = "FacadeSample"
    config_prefix: str = "fac_"
    app: AppLogicSample

    def constructConfigModel(self) -> FacadeSampleConfigModel:
        return FacadeSampleConfigModel.model_construct(_validate=False)

    def initializeRouters(self):
        """All routers (built-in or external) must be initialized at this step"""
        self.initializeKafkaRouter(handlerFunc=self.app.SampleCall,
                                   start_immediately=False)

    def start(self):
        self.ctx.logger.debug(f"Facade configuration:\n{self.config.model_dump_json(indent=4)}")
        self.ctx.logger.debug(f"Facade starting: {self.name}")
        self.app = AppLogicSample(self.ctx)
