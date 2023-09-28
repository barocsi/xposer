import asyncio

from pydantic import Field

from xposer.api.base.base_fastapi_service import BaseFastApiService
from xposer.api.base.base_fastapi_service_config_model import BaseFastApiRouterConfigModel
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.core.configure import Configurator
from xposer.sample_app.http_post_uvicorn_fastapi.routers.sample_app_http_service import SampleAppHTTPService
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http import SampleAppHTTP


class SampleAppHttpFacadeConfigModel(BaseFastApiRouterConfigModel):
    foo_param: str = Field(default='foo')
    uvicorn_host: str = Field(default='localhost')
    uvicorn_port: int = Field(default=8000)


class SampleAppHttpFacade(FacadeBaseClass):
    config_prefix: str = "xpfacade_"
    api_prefix: str = "/api"
    app: SampleAppHTTP = None
    fastapi_router: SampleAppHTTPService = None
    facade_conf_class: SampleAppHttpFacadeConfigModel

    def mergeConfigurationFromPrefix(self) -> SampleAppHttpFacadeConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppHttpFacadeConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix,
                                                      validate=True,
                                                      strict=True)

    def handle_task_exception(self, task):
        try:
            # This will re-raise the exception if one occurred.
            task.result()
        except asyncio.TimeoutError:
            raise ValueError("The service did not start within 30 seconds!")

    async def startFacadeServices(self):
        self.http_router = BaseFastApiService(self.ctx)
        routes = self.app.provideRoutes()
        future = asyncio.Future()
        await self.http_router.startService(
            self.config.uvicorn_host,
            self.config.uvicorn_port,
            routes,
            api_prefix=self.api_prefix
        )

    async def initializeApps(self):
        # SampleAppHttp does not have any specific method
        self.app = SampleAppHTTP(self.ctx)

    def afterInititalization(self):
        self.ctx.logger.debug(f"Facade starting")
