import asyncio
from typing import List

from pydantic import ConfigDict, Field

from xposer.api.base.base_kafka_service_config_model import BaseKafkaServiceConfigModel
from xposer.api.base.base_service import BaseService
from xposer.api.base.xpcontroller_base_class import XPControllerBaseClass
from xposer.core.configure import Configurator
from xposer.sample_app.rpc_kafka.sample_app_kafka import SampleAppKafka
from xposer.sample_app.rpc_kafka.sample_app_kafka_service import SampleAppKafkaService


class SampleAppKafkaXPControllerConfigModel(BaseKafkaServiceConfigModel):
    foo: str = Field(default='foo',
                     description="Some xpcontroller specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class SampleAppKafkaXPController(XPControllerBaseClass):
    config_prefix: str = "xpcontroller_"
    app: SampleAppKafka = None
    xpcontroller_conf_class: SampleAppKafkaXPControllerConfigModel
    routers: List[BaseService] = []

    def mergeConfigurationFromPrefix(self) -> SampleAppKafkaXPControllerConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppKafkaXPControllerConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix,
                                                      validate=True,
                                                      strict=True)

    async def initializeApps(self):
        self.app = SampleAppKafka(self.ctx)

    async def start_kafka_service(self, callback):
        await self.kafka_service.start_service(app=self.app,
                                               server_string=self.config.router_kafka_server_string,
                                               group_id=self.config.router_kafka_group_id,
                                               inbound_topic=self.config.router_kafka_inbound_topic,
                                               outbound_topic=self.config.router_kafka_outbound_topic,
                                               exception_topic=self.config.router_kafka_exception_topic,
                                               handler_func=self.app.RPCHandler,
                                               produce_on_result=True,
                                               callback=callback)

    def handle_task_exception(self, task):
        try:
            # This will re-raise the exception if one occurred.
            task.result()
        except asyncio.TimeoutError:
            ...
            # raise ValueError("The service did not start within 30 seconds!")

    async def startXPControllerServices(self):
        self.kafka_service = SampleAppKafkaService(self.ctx)
        self.routers.append(self.kafka_service)
        future = asyncio.Future()
        kafka_service_task = asyncio.create_task(self.start_kafka_service(callback=future.set_result))
        kafka_service_task.set_name("SampleAppKafkaXPController:KafkaServiceTask")
        timeout_task = asyncio.create_task(asyncio.wait_for(future, timeout=30))
        timeout_task.set_name("SampleAppKafkaXPController:KafkaServiceTimeoutTask")
        timeout_task.add_done_callback(self.handle_task_exception)

    def afterInititalization(self):
        self.ctx.logger.debug(f"XPController starting")
