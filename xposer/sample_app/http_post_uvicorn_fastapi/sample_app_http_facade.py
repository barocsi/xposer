from pydantic import Field, ConfigDict

from xposer.api.base.base_fastapi_router_config_model import BaseFastApiRouterConfigModel
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http import SampleAppHTTP
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http_router import SampleSampleAppHTTPRouter


class SampleAppHttpConfigModel(BaseFastApiRouterConfigModel):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class SampleAppHttpFacade(FacadeBaseClass):
    config_prefix: str = "facfast_"
    app: SampleAppHTTP = None

    def constructConfigModel(self) -> SampleAppHttpConfigModel:
        return SampleAppHttpConfigModel.model_construct(_validate=False)

    def initializeRouters(self):
        self.http_router = SampleSampleAppHTTPRouter(self.ctx, self.api, self.app)

    def initializeAppsBeforeRouters(self):
        self.app = SampleAppHTTP(self.ctx)

    def afterInititalization(self):
        self.ctx.logger.debug(f"Facade configuration:\n{self.config.model_dump_json(indent=4)}")
        self.ctx.logger.debug(f"Facade starting: {self.__class__.__name__}")
