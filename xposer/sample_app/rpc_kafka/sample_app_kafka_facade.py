from pydantic import ConfigDict, Field
import asyncio
from xposer.api.base.base_kafka_router_config_model import BaseKafkaRouterConfigModel
from xposer.api.base.facade_base_class import FacadeBaseClass
from xposer.core.configure import Configurator
from xposer.sample_app.rpc_kafka.sample_app_kafka import SampleAppKafka
from xposer.sample_app.rpc_kafka.sample_app_kafka_router import SampleAppKafkaRouter


class SampleAppKafkaFacadeConfigModel(BaseKafkaRouterConfigModel):
    foo: str = Field(default='foo',
                     description="Some facade specific config")
    bar: str = Field('bar')
    model_config = ConfigDict(extra='allow')


class SampleAppKafkaFacade(FacadeBaseClass):
    config_prefix: str = "xpfacade_"
    app: SampleAppKafka = None
    facade_conf_class: SampleAppKafkaFacadeConfigModel

    def mergeConfigurationFromPrefix(self) -> SampleAppKafkaFacadeConfigModel:
        return Configurator.mergeAttributesWithPrefix(SampleAppKafkaFacadeConfigModel,
                                                      self.ctx.config,
                                                      self.config_prefix)

    def initializeAppsBeforeRouters(self):
        self.app = SampleAppKafka(self.ctx)

    def initializeRouters(self):
        self.kafka_router = SampleAppKafkaRouter(self.ctx)
        asyncio.create_task(self.kafka_router.start_router(app=self.app,
                                                          server_string=self.config.router_kafka_server_string,
                                                          group_id=self.config.router_kafka_group_id,
                                                          inbound_topic=self.config.router_kafka_inbound_topic,
                                                          outbound_topic=self.config.router_kafka_outbound_topic,
                                                          exception_topic=self.config.router_kafka_exception_topic,
                                                          handler_func=self.app.RPCHandler,
                                                          produce_on_result=True))

    def afterInititalization(self):
        self.ctx.logger.debug(f"Facade starting: {self.__class__.__name__}")
