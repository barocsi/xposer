import asyncio
import inspect
import json
from typing import Callable

from xposer.api.base.base_kafka_aiolib import AIOConsumer, AIOProducer
from xposer.api.base.base_service import BaseService
from xposer.core.context import Context


class BaseKafkaService(BaseService):

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        _cancelled: bool = False

    async def start_service(self,
                            server_string: str,
                            group_id: str,
                            inbound_topic: str,
                            outbound_topic: str,
                            exception_topic: str,
                            handler_func: Callable = None,
                            produce_on_result: bool = False):

        self._cancelled = False

        if not inspect.iscoroutinefunction(handler_func):
            raise TypeError("handler_func must be an asynchronous coroutine function")

        consumer_config = {
            'bootstrap.servers': server_string,
            'group.id': group_id,
            'auto.offset.reset': 'latest',
            'fetch.message.max.bytes': '1048576',
            'fetch.wait.max.ms': '10',
            'heartbeat.interval.ms': '1000',
            'session.timeout.ms': '6000',
            'enable.auto.commit': False
        }
        producer_config = {
            'bootstrap.servers': server_string,
        }

        async def consumer_handler_func(data):
            """Warning: This is non thread-safe"""
            correlation_id = None
            if isinstance(data, dict):
                correlation_id = data.get('correlation_id', 'N/A')
            try:
                processed_data = await handler_func(data)
                response = {
                    'result': processed_data,
                    'correlation_id': correlation_id
                }
                if produce_on_result:
                    try:
                        await self._producer.produce(outbound_topic, json.dumps(response))
                        self.ctx.logger.debug("Message produced successfully!")
                    except Exception as e:
                        self.ctx.logger.exception(f"Error producing message: {e}")
            except Exception as e:
                if exception_topic is not None:
                    exception_data = {
                        'exception': str(e),
                        'correlation_id': correlation_id
                    }
                    await self._producer.produce(exception_topic, json.dumps(exception_data))

        # Initiate AIOProducer and AIOConsumer
        self._producer = AIOProducer(producer_config)
        self._consumer = AIOConsumer(consumer_config,
                                     consumer_handler_func,
                                     inbound_topics=[inbound_topic],
                                     exception_queue=self.ctx.exception_queue)
        self.ctx.logger.info(f"Service initialized successfully. Listening on topic: {inbound_topic}.")

    async def stop_router(self):
        self.ctx.logger.info(f"Shutting down service")
        self._producer.close()
        self._consumer.close()

        # Stop all running asyncio tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
