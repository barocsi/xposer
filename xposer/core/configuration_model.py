import logging

from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class ConfigModel(BaseSettings):
    log_to_console_enabled: bool = Field(True,
                                         error_messages={
                                             'type_error': 'The host must be boolean.'
                                         })
    log_to_console_loglevel: int | str = Field(logging.DEBUG,
                                               error_messages={
                                                   'type_error': 'The host must be int.'
                                               })
    log_to_kafka_enabled: bool = Field(True,
                                       error_messages={
                                           'type_error': 'The host must be boolean.'
                                       })
    log_to_kafka_server_string: str = Field('localhost:9092',
                                            error_messages={
                                                'type_error': 'The host must be string.'
                                            })
    log_to_kafka_server_log_topic: str = Field('log',
                                               error_messages={
                                                   'type_error': 'The host must be string.'
                                               })
    domain_facade_id: str = Field('default',
                                  error_messages={
                                      'type_error': 'The host must be string.'
                                  })

    model_config = ConfigDict(extra='allow')

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
