import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from xposer.core.boot import Boot
from xposer.core.configure import Configurator
from xposer.core.context import Context


class SampleAppHTTPItem(BaseModel):
    username: str
    email: str


class SampleAppHTTPConfigModel(BaseSettings):
    logic_param: str = Field(default="logic_param_example_default_value")
    logic_param_to_override: str = Field(default="not_ovverridden")
    uvicorn_host: str = Field(default="0.0.0.0")
    uvicorn_port: int = Field(default=8000)
    model_config = ConfigDict(extra='allow')


class SampleAppHTTP:
    ctx: Context
    config: SampleAppHTTPConfigModel
    config_prefix: str = "xp_app_internal"

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.config = Configurator.mergeAttributesWithPrefix(SampleAppHTTPConfigModel, ctx.config, self.config_prefix)
        self.ctx.logger.debug(f"Initialized {self.__class__.__name__} "
                              f"parameters:\n{self.config.model_dump_json(indent=4)}")


def main():
    ctx: Context = Boot.boot()
    facade = ctx.facade
    fast_api_reference: FastAPI = facade.http_router.api
    app: SampleAppHTTP = facade.app
    config:SampleAppHTTPConfigModel = app.config

    if not isinstance(fast_api_reference, FastAPI):
        raise TypeError(f"Expected instance of FastAPI, got {type(fast_api_reference)}")

    uvicorn.run(fast_api_reference, host=app.config.uvicorn_host, port=app.config.uvicorn_port)


if __name__ == "__main__":
    main()
