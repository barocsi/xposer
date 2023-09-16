from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class BaseFastApiRouterConfigModel(BaseSettings):
    router_fastapi_foo: str = Field(default="bar",
                                    description="Some basic uvicorn and fastapi parameters can go here")
    model_config = ConfigDict(extra='allow')
