import json

from confluent_kafka import Consumer, Producer


class BaseKafkaRouter:

    def __init__(self,
                 consumer_config,
                 producer_config,
                 inbound_topic,
                 outbound_topic,
                 exception_topic,
                 handler_func,
                 produce_on_result):
        self.consumer = Consumer(consumer_config)
        self.producer = Producer(producer_config)
        self.inbound_topic = inbound_topic
        self.outbound_topic = outbound_topic
        self.exception_topic = exception_topic
        self.handler_func = handler_func
        self.produce_on_result = produce_on_result
        self.consumer.subscribe([inbound_topic])

    def start(self):
        while True:
            msg = self.consumer.poll(1)
            correlation_id = None
            if msg:
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    correlation_id = data.get('correlation_id', 'N/A')
                    processed_data = self.handler_func(data)
                    response = {
                        'result': processed_data,
                        'correlation_id': correlation_id  # Include the correlation ID in the response
                    }
                    self.producer.produce(self.outbound_topic, json.dumps(response))
                except Exception as e:
                    if self.exception_topic is not None:
                        exception_data = {
                            'exception': str(e),
                            'correlation_id': correlation_id  # Include the correlation ID in the exception response
                        }
                        self.producer.produce(self.exception_topic, json.dumps(exception_data))
