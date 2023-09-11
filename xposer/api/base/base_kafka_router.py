import asyncio
import json
from typing import Any, Callable

from confluent_kafka import Consumer, Producer

from xposer.api.base.base_router import BaseRouter


class BaseKafkaRouter(BaseRouter):
    async def start_router(self,
                          app: Any,
                          server_string: str,
                          group_id: str,
                          inbound_topic: str,
                          outbound_topic: str,
                          exception_topic: str,
                          handler_func: Callable = None,
                          produce_on_result: bool = False):

        consumer_config = {
            'bootstrap.servers': server_string,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        producer_config = {
            'bootstrap.servers': server_string
        }

        consumer = Consumer(consumer_config)
        producer = Producer(producer_config)
        consumer.subscribe([inbound_topic])

        loop = asyncio.get_event_loop()

        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1)
            correlation_id = None
            if msg:
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    correlation_id = data.get('correlation_id', 'N/A')
                    processed_data = handler_func(data)
                    response = {
                        'result': processed_data,
                        'correlation_id': correlation_id
                    }
                    if produce_on_result:
                        await loop.run_in_executor(None, producer.produce, outbound_topic, json.dumps(response))
                except Exception as e:
                    if exception_topic is not None:
                        exception_data = {
                            'exception': str(e),
                            'correlation_id': correlation_id
                        }
                        self.ctx.logger.exception(e)
                        await loop.run_in_executor(None, producer.produce, exception_topic, json.dumps(exception_data))
