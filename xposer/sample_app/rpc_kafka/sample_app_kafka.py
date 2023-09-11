import json
from dataclasses import Field
from typing import Any

from pydantic_settings import BaseSettings

from xposer.core.boot import Boot
from xposer.core.configure import Configurator
from xposer.core.context import Context


class SampleAppKafkaConfigModel(BaseSettings):
    logic_param: str = Field(default="logic_param_example_default_value")
    logic_param_to_override: str = Field(default="not_ovverridden")


class SampleAppKafka:
    ctx: Context
    config: SampleAppKafkaConfigModel
    config_prefix: str = "xp_app_internal"

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.config = Configurator.mergeAttributesWithPrefix(SampleAppKafkaConfigModel, ctx.config,
                                                             self.config_prefix)
        self.ctx.logger.debug(f"Initialized {self.__class__.__name__} "
                              f"with configuration parameters:\n{self.config.model_dump_json(indent=4)}")

    def RPCHandler(self, data: Any):
        self.ctx.logger.info(
            f"Sample call with correlation id:{data.get('correlation_id', 'None')} receives sample raw data:\n{json.dumps(data, indent=4)}")
        return json.dumps({"result": "whoa", "originalfoo": data.get('foo', 'None')})


def main():
    # Load and boot facade
    Boot.boot()


if __name__ == "__main__":
    main()
