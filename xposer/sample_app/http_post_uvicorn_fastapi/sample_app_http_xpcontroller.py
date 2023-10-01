import asyncio
import os

from pydantic import Field

from xposer.api.base.base_fastapi_service import BaseFastApiService
from xposer.api.base.base_fastapi_service_config_model import BaseFastApiRouterConfigModel
from xposer.api.base.xpcontroller_base_class import XPControllerBaseClass
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.sample_app.http_post_uvicorn_fastapi.routers.sample_app_http_service import SampleAppHTTPService


class SampleAppHttpControllerConfigModel(BaseFastApiRouterConfigModel):
    foo_param: str = Field(default='foo')
    uvicorn_host: str = Field(default='localhost')
    uvicorn_port: int = Field(default=8000)


class SampleAppHttpXPController(XPControllerBaseClass):

    def __init__(self, ctx: Context):
        self.config_prefix: str = "xpcontroller_"
        self.api_prefix: str = "/api"
        self.uvicorn_server = None
        self.fastapi_router: SampleAppHTTPService = None
        self.xpcontroller_conf_class: SampleAppHttpControllerConfigModel
        super().__init__(ctx)

    def mergeConfigurationFromPrefix(self) -> SampleAppHttpControllerConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppHttpControllerConfigModel,
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

    async def start_fastapi_service(self, callback):
        self.uvicorn_server = await self.http_router.startService(
            self.config.uvicorn_host,
            self.config.uvicorn_port,
            [SampleAppHTTPService.getRoute(self.ctx)],
            api_prefix=self.api_prefix,
            callback=callback,
        )

    async def tearDownXPController(self):
        self.uvicorn_server.should_exit = True
        await asyncio.sleep(1)


    async def startXPControllerServices(self):
        self.http_router = BaseFastApiService(self.ctx)
        future = asyncio.Future()
        asyncio.create_task(self.start_fastapi_service(callback=None))
        task = asyncio.create_task(asyncio.wait_for(future, timeout=3))
        task.add_done_callback(self.handle_task_exception)


    def afterInititalization(self):
        self.ctx.logger.debug(f"XPController starting")
