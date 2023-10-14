import logging

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class ConfigModel(BaseSettings):
    debug_enabled_for_built_in_http: bool = Field(default=True,
                                         error_messages={
                                         })
    log_to_console_enabled: bool = Field(default=True,
                                         error_messages={
                                         })
    log_to_console_loglevel: int | str = Field(logging.DEBUG,
                                               error_messages={
                                               })
    log_to_kafka_enabled: bool = Field(default=True,
                                       error_messages={
                                       })
    log_to_kafka_server_string: str = Field('localhost:9092',
                                            error_messages={
                                            })
    log_to_kafka_server_log_topic: str = Field('log',
                                               error_messages={
                                               })
    xpcontroller_module_name: str | None = Field(...,
                                                 error_messages={
                                                 })
    xpcontroller_class_name: str | None = Field(...,
                                                error_messages={
                                                })

    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)

    @field_validator('log_to_console_loglevel')
    def map_log_level(cls, value):
        if isinstance(value, str):
            level = getattr(logging, value.upper(), None)
            if isinstance(level, int):
                return level
            else:
                raise ValueError("Invalid log level name.")
        elif isinstance(value, int):
            return value
        else:
            raise TypeError("Invalid log level type.")
