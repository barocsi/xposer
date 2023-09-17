import asyncio
from typing import List

from pydantic import ConfigDict, Field

from xposer.api.base.base_kafka_service_config_model import BaseKafkaServiceConfigModel
from xposer.api.base.base_service import BaseService
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.core.configure import Configurator
from xposer.sample_app.rpc_kafka.sample_app_kafka import SampleAppKafka
from xposer.sample_app.rpc_kafka.sample_app_kafka_router import SampleAppKafkaRouter


class SampleAppKafkaFacadeConfigModel(BaseKafkaServiceConfigModel):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class SampleAppKafkaFacade(FacadeBaseClass):
    config_prefix: str = "xpfacade_"
    app: SampleAppKafka = None
    facade_conf_class: SampleAppKafkaFacadeConfigModel
    routers: List[BaseService] = []

    def mergeConfigurationFromPrefix(self) -> SampleAppKafkaFacadeConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppKafkaFacadeConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix,
                                                      validate=True,
                                                      strict=True)

    async def initializeApps(self):
        self.app = SampleAppKafka(self.ctx)

    async def start_kafka_router(self, callback):
        await self.kafka_router.start_router(app=self.app,
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
            #raise ValueError("The service did not start within 30 seconds!")

    async def startServices(self):
        self.kafka_router = SampleAppKafkaRouter(self.ctx)
        self.routers.append(self.kafka_router)
        future = asyncio.Future()
        asyncio.create_task(self.start_kafka_router(callback=future.set_result))
        task = asyncio.create_task(asyncio.wait_for(future, timeout=30))
        task.add_done_callback(self.handle_task_exception)

    def afterInititalization(self):
        self.ctx.logger.debug(f"Facade starting")
