import json
from typing import Any

from pydantic_settings import BaseSettings

from xposer.core.boot import Boot
from xposer.core.configure import Configurator
from xposer.core.context import Context


class SampleAppKafkaConfigModel(BaseSettings):
    logic_param: str = "some_app_param"
    logic_param_to_override: str = " jens"


class SampleAppKafka:
    ctx: Context
    config: SampleAppKafkaConfigModel

    def __init__(self, ctx: Context):
        self.ctx = ctx
        app_config_defaults = SampleAppKafkaConfigModel.model_construct(_validate=False)
        app_config_merged = Configurator.mergePrefixedAttributes(app_config_defaults, ctx.config, 'app_kafka_logic_')
        app_config_merged.model_validate(app_config_merged)
        self.config = app_config_merged
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
