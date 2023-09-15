import json
from typing import Any

from pydantic import Field
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
    config_prefix: str = "xpapp_"

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.config = Configurator.mergeAttributesWithPrefix(SampleAppKafkaConfigModel,
                                                             ctx.config,
                                                             self.config_prefix)
        self.ctx.logger.info(f"Initialized {self.__class__.__name__}")

    def RPCHandler(self, data: Any):
        self.ctx.logger.info(
            f"Sample call with correlation id:{data.get('correlation_id', 'None')} receives sample raw data:\n{json.dumps(data, indent=4)}")
        return json.dumps({"result": "whoa", "originalfoo": data.get('foo', 'None')})


def main():
    # Load and boot facade
    boot_manager = Boot().boot()


if __name__ == "__main__":
    main()
