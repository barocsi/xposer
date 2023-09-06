import sys
import os

#sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from xposer.core.boot import Boot
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from xposer.core.configure import Configurator
from xposer.core.context import Context


class AppSubDTO(BaseModel):
    username: str
    email: str


class AppSubConfigModel(BaseSettings):
    logic_param: str = "some_app_param"
    logic_param_to_override: str = " jens"


class AppSub:
    ctx: Context
    config: AppSubConfigModel

    def __init__(self, ctx: Context):
        self.ctx = ctx
        app_config_defaults = AppSubConfigModel.model_construct(_validate=False)
        app_config_merged = Configurator.mergePrefixedAttributes(app_config_defaults, ctx.config, 'app_')
        app_config_merged.model_validate(app_config_merged)
        self.config = app_config_merged
        self.ctx.logger.debug(f"Initialized {self.__class__.__name__} "
                              f"with configuration parameters:\n{self.config.model_dump_json(indent=4)}")

    def SampleCall(self, some_data):
        self.ctx.logger.info(f"Sample call receives sample raw data:\n{some_data.model_dump_json(indent=4)}")


def main():
    Boot.boot()


if __name__ == "__main__":
    main()
