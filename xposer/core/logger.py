import inspect
import logging

from confluent_kafka import Producer

from xposer.core.configuration_model import ConfigModel

class XposeLogger(logging.Logger):
    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)
        record.classname = 'UNKNOWN'

        frames = inspect.stack()
        for frame in frames:
            instance = frame[0].f_locals.get('self')
            if instance:
                record.classname = instance.__class__.__name__
                break

        return record


logging.setLoggerClass(XposeLogger)


class KafkaLoggingHandler(logging.Handler):
    def __init__(self, kafka_producer, topic_map):
        logging.Handler.__init__(self)
        self.kafka_producer = kafka_producer
        self.topic_map = topic_map

    def emit(self, record):
        msg = self.format(record)
        topic = self.topic_map.get(record.levelname, 'debug_topic')
        self.kafka_producer.produce(topic, msg)


def get_logger(appConfig: ConfigModel):
    logger_name = "xpose_logger"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # Console Handler
    if appConfig.log_to_console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(classname)s] -  %(message)s')
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
        logger.debug(f"Logger initialized: {logger.name}")

    return logger
