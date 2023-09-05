import logging

from confluent_kafka import Producer

from xposer.models.configuration_model import ConfigModel


class KafkaLoggingHandler(logging.Handler):
    def __init__(self, kafka_producer, topic_map):
        logging.Handler.__init__(self)
        self.kafka_producer = kafka_producer
        self.topic_map = topic_map

    def emit(self, record):
        msg = self.format(record)
        topic = self.topic_map.get(record.levelname, 'default_topic')
        self.kafka_producer.produce(topic, msg)


def get_logger(appConfig: ConfigModel):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console Handler
    if appConfig.log_to_console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Kafka Handler
    if appConfig.log_to_kafka_enabled:
        kafka_config = {
            'bootstrap.servers': appConfig.log_to_kafka_server_string
        }
        producer = Producer(kafka_config)
        topic_map = {
            'DEBUG': 'debug_topic',
            'INFO': 'info_topic',
            'WARNING': 'warning_topic',
            'ERROR': 'error_topic',
            'CRITICAL': 'critical_topic'
        }
        kafka_handler = KafkaLoggingHandler(producer, topic_map)
        kafka_handler.setLevel(logging.DEBUG)
        kafka_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        kafka_handler.setFormatter(kafka_formatter)
        logger.addHandler(kafka_handler)

    return logger
