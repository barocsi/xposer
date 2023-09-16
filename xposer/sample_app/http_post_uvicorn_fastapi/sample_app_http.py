import asyncio

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from xposer.core.boot import Boot
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.sample_app.http_post_uvicorn_fastapi.routers.sample_app_http_router import SampleAppHTTPRouter


class SampleAppHTTPItem(BaseModel):
    username: str
    email: str


class SampleAppHTTPConfigModel(BaseSettings):
    logic_param: str = Field(default="logic_param_example_default_value")
    logic_param_to_override: str = Field(default="not_overridden")
    uvicorn_host: str = Field(default="0.0.0.0")
    uvicorn_port: int = Field(default=8000)
    model_config = ConfigDict(extra='allow')


class SampleAppHTTP:
    ctx: Context
    config: SampleAppHTTPConfigModel
    config_prefix: str = "xpapp_"

    def __init__(self, ctx: Context):
        self.ctx = ctx

        self.config = Configurator.mergeAttributesWithPrefix(SampleAppHTTPConfigModel,
                                                             ctx.config,
                                                             self.config_prefix,
                                                             validate=True,
                                                             strict=True)
        self.ctx.logger.info(f"Initialized application")

    def provideRoutes(self):
        routes = SampleAppHTTPRouter.getRoute(self.ctx)
        return [routes]


async def main():
    await Boot().boot()


if __name__ == "__main__":
    asyncio.run(main())
