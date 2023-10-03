import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from confluent_kafka import Consumer, KafkaException, Producer


class AIOProducer:
    def __init__(self, configs, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = Producer(configs)
        self._cancelled = False
        self._poll_task = self._loop.create_task(self._poll_loop())
        self._poll_task.set_name("AIOProducer::Poll")

    async def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)
            await asyncio.sleep(0.1)

    def close(self):
        self._cancelled = True
        self._producer.flush()
        if self._poll_task:  # Ensure the task is available before trying to cancel
            self._poll_task.cancel()
            self._producer.flush()

    async def produce(self, topic, value):
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                result.set_exception(KafkaException(err))
            else:
                result.set_result(msg)

        self._producer.produce(topic, value, on_delivery=ack)

        return await result


class AIOConsumer:
    def __init__(self,
                 configs,
                 handler_func,
                 inbound_topics: list,
                 exception_queue: Queue,
                 loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._consumer = Consumer(configs)
        self._exception_queue = exception_queue
        self._consumer.subscribe(inbound_topics)
        self._handler_func = handler_func
        self._cancelled = False
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._consume_task = self._loop.create_task(self._consume_loop())
        self._consume_task.set_name("AIOConsumer::Consume")

    async def _handle_and_commit(self, msg):
        raw_value = msg.value().decode('utf-8') if msg.value() else None
        try:
            data = json.loads(raw_value)
        except json.JSONDecodeError:
            data = raw_value  # Continue with the raw string if it's not JSON-decodable

        if not data:
            raise Exception("Missing value from the message", msg)

        await self._handler_func(data)
        self._consumer.commit(message=msg)

    async def _consume_loop(self):
        while not self._cancelled:
            try:
                msg = await self._loop.run_in_executor(self._executor, self._consumer.poll, 0.1)
                if msg:
                    await self._handle_and_commit(msg)
            except Exception as e:
                if self._exception_queue:
                    self._exception_queue.put_nowait(e)

    def close(self):
        self._cancelled = True
        self._executor.shutdown()
        if self._consume_task:
            self._consume_task.cancel()
