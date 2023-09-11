from pydantic import Field

from xposer.api.base.base_fastapi_router_config_model import BaseFastApiRouterConfigModel
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.core.configure import Configurator
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http import SampleAppHTTP
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http_router import SampleSampleAppHTTPRouter


class SampleAppHttpFacadeConfigModel(BaseFastApiRouterConfigModel):
    foo_param: str = Field(default='foo')


class SampleAppHttpFacade(FacadeBaseClass):
    config_prefix: str = "xp_app_facade_"
    api_prefix: str = "/api"
    app: SampleAppHTTP = None
    http_router: SampleSampleAppHTTPRouter = None
    facade_conf_class: SampleAppHttpFacadeConfigModel

    def mergeConfigurationFromPrefix(self) -> SampleAppHttpFacadeConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppHttpFacadeConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix)

    def initializeRouters(self):
        self.http_router = SampleSampleAppHTTPRouter(self.ctx)
        self.http_router.start_router(api_prefix=self.api_prefix)

    def initializeAppsBeforeRouters(self):
        self.app = SampleAppHTTP(self.ctx)

    def afterInititalization(self):
        self.ctx.logger.debug(f"Facade configuration:\n{self.config.model_dump_json(indent=4)}")
        self.ctx.logger.debug(f"Facade starting: {self.__class__.__name__}")
