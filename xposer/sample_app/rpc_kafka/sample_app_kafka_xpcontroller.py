import asyncio
import json
from typing import Any, List

from pydantic import ConfigDict, Field

from xposer.api.base.base_kafka_service import BaseKafkaService
from xposer.api.base.base_kafka_service_config_model import BaseKafkaServiceConfigModel
from xposer.api.base.base_service import BaseService
from xposer.api.base.xpcontroller_base_class import XPControllerBaseClass
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.sample_app.rpc_kafka.sample_app_kafka import SampleAppKafka
from xposer.sample_app.rpc_kafka.sample_app_kafka_service import SampleAppKafkaService


class SampleAppKafkaXPControllerConfigModel(BaseKafkaServiceConfigModel):
    foo: str = Field(default='foo',
                     description="Some xpcontroller specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class SampleAppKafkaXPController(XPControllerBaseClass):

    def __init__(self, ctx: Context):
        self.config_prefix: str = "xpcontroller_"
        self.kafka_router: BaseKafkaService | Any = None
        xpcontroller_conf_class: SampleAppKafkaXPControllerConfigModel
        super().__init__(ctx)

    def mergeConfigurationFromPrefix(self) -> SampleAppKafkaXPControllerConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppKafkaXPControllerConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix,
                                                      validate=True,
                                                      strict=True)

    async def RPCHandler(self, data: Any):
        self.ctx.logger.info(
            f"Sample call with correlation id:{data.get('correlation_id', 'None')} receives sample raw data:\n{json.dumps(data, indent=4)}")
        return json.dumps({"result": "whoa", "originalfoo": data.get('foo', 'None')})

    async def start_kafka_service(self, callback):
        try:
            await self.kafka_service.start_service(
                server_string=self.config.router_kafka_server_string,
                group_id=self.config.router_kafka_group_id,
                inbound_topic=self.config.router_kafka_inbound_topic,
                outbound_topic=self.config.router_kafka_outbound_topic,
                exception_topic=self.config.router_kafka_exception_topic,
                handler_func=self.RPCHandler,
                produce_on_result=True)
            callback(None)
        except Exception as e:
            # Log the exception for debugging
            self.ctx.logger.exception(f"Error starting kafka service: {e}")
            # Notify the future object about the failure
            raise

    def handle_task_exception(self, task):
        try:
            task.result()
        except asyncio.TimeoutError:
            ...
            raise ValueError("The service did not start within 30 seconds!")

    async def tearDownXPControllerServices(self):
        ...

    async def startXPControllerServices(self):
        self.kafka_service = SampleAppKafkaService(self.ctx)
        future = asyncio.Future()
        kafka_service_task = asyncio.create_task(self.start_kafka_service(callback=future.set_result))
        kafka_service_task.set_name("SampleAppKafkaXPController:KafkaServiceTask")
        timeout_task = asyncio.create_task(asyncio.wait_for(future, timeout=3))
        timeout_task.set_name("SampleAppKafkaXPController:KafkaServiceTimeoutTask")
        timeout_task.add_done_callback(self.handle_task_exception)
        await future

    def afterInititalization(self):
        self.ctx.logger.debug(f"XPController starting")
