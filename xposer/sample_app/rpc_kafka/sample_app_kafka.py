import asyncio
import json
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings

from xposer.core.boot import Boot
from xposer.core.configure import Configurator
from xposer.core.context import Context


class SampleAppKafkaConfigModel(BaseSettings):
    logic_param: str = Field(default="logic_param_example_default_value")
    logic_param_to_override: str = Field(default="not_overridden")


class SampleAppKafka:
    ctx: Context
    config: SampleAppKafkaConfigModel
    config_prefix: str = "xpapp_"

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.config = Configurator.mergeAttributesWithPrefix(SampleAppKafkaConfigModel,
                                                             ctx.config,
                                                             self.config_prefix,
                                                             validate=True,
                                                             strict=True
                                                             )
        self.ctx.logger.info(f"Initialized application")

    async def RPCHandler(self, data: Any):
        self.ctx.logger.info(
            f"Sample call with correlation id:{data.get('correlation_id', 'None')} receives sample raw data:\n{json.dumps(data, indent=4)}")
        return json.dumps({"result": "whoa", "originalfoo": data.get('foo', 'None')})


async def main():
    await Boot().boot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) != 'Event loop stopped before Future completed.':
            raise
