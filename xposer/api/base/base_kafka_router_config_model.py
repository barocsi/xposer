from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class BaseKafkaRouterConfigModel(BaseSettings):
    router_kafka_inbound_topic: str = Field(default="router_inbound",
                                            description="Default topicname the router should listen to")
    router_kafka_outbound_topic: str = Field(default="router_outbound",
                                             description="Default topicname the router should publish results to")
    router_kafka_exception_topic: str = Field(default="router_exception",
                                              description="Default topicname the router should throw exceptions")
    router_kafka_server_string: str = "localhost:9092"
    router_kafka_group_id: str = "routers"

    model_config = ConfigDict(extra='allow')
