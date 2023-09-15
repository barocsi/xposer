import asyncio
import json
from threading import Event, Thread
from typing import Any, Callable

from xposer.api.base.base_kafka_aiolib import AIOConsumer, AIOProducer
from xposer.api.base.base_router import BaseRouter


class BaseKafkaRouter(BaseRouter):
    _thread: Thread = None
    _cancelled: bool = False
    _loop: any = None

    def _run_in_thread(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._event.set()
        self._loop.run_forever()

    def start_router(self,
                     app: Any,
                     server_string: str,
                     group_id: str,
                     inbound_topic: str,
                     outbound_topic: str,
                     exception_topic: str,
                     handler_func: Callable = None,
                     produce_on_result: bool = False):

        self._cancelled = False
        # We must wait for thread initialization and to access the thread newly created loop
        self._event = Event()
        self._thread = Thread(target=self._run_in_thread)
        self._thread.start()
        self._event.wait()

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

        def consumer_handler_func(data):
            correlation_id = data.get('correlation_id', 'N/A')
            try:
                processed_data = handler_func(data)
                response = {
                    'result': processed_data,
                    'correlation_id': correlation_id
                }
                if produce_on_result:
                    async def produce_async():
                        try:
                            await self._producer.produce(outbound_topic, json.dumps(response))
                            self.ctx.logger.debug("Message produced successfully!")
                        except Exception as e:
                            self.ctx.logger.exception(f"Error producing message: {e}")

                    self._loop.call_soon_threadsafe(asyncio.create_task, produce_async())
            except Exception as e:
                if exception_topic is not None:
                    exception_data = {
                        'exception': str(e),
                        'correlation_id': correlation_id
                    }
                    print("Exception")
                    self._loop.call_soon_threadsafe(asyncio.create_task,
                                                    self._producer.produce(exception_topic, json.dumps(exception_data)))

        # Initiate AIOProducer and AIOConsumer with the event loop specific to this router instance
        self._producer = AIOProducer(consumer_config, loop=self._loop)
        self._consumer = AIOConsumer(consumer_config, consumer_handler_func, inbound_topics=[inbound_topic],
                                     loop=self._loop)
        self.ctx.logger.info(f"Router {self.__class__} initialized successfully. Listening on topic: {inbound_topic}.")

    def stop_router(self):
        self.ctx.logger.info(f"Shutting down router: {self.__class__}")
        event = Event()
        self._cancelled = True
        self._producer.close()
        self._consumer.close()

        # Stop all running asyncio tasks associated with this router's event loop
        tasks = [t for t in asyncio.all_tasks(self._loop) if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        self._loop.call_soon_threadsafe(self._loop.stop)  # Stop the event loop in thread-safe manner
        self._thread.join()  # Wait for the thread to finish
