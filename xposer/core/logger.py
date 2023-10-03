import json
import logging
import os
import sys
from confluent_kafka import Producer
from xposer.core.configuration_model import ConfigModel

currentframe = lambda: sys._getframe(3)
_logging_srcfile = os.path.normcase(logging.addLevelName.__code__.co_filename)
_this_srcfile = __file__


class XposeLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def findCaller(self, stack_info=None, stacklevel=None):
        f = currentframe()
        rv = "(unknown file)", 0, "(unknown function)"
        while f and hasattr(f, "f_code"):
            co, filename = f.f_code, os.path.normcase(f.f_code.co_filename)
            if co.co_name != 'test_logging' and filename in [_logging_srcfile, _this_srcfile]:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)
        filename, lineno, funcName = self.findCaller()
        short_fn = os.path.basename(filename) if len(filename.split(os.sep)) <= 2 else f"{filename.split(os.sep)[-3]}/{os.path.basename(filename)}"
        record.filename, record.lineno, record.funcName = short_fn, lineno, funcName
        return record


logging.setLoggerClass(XposeLogger)


class KafkaLoggingHandler(logging.Handler):
    def __init__(self, kafka_producer, topic_map):
        super().__init__()
        self.kafka_producer, self.topic_map = kafka_producer, topic_map

    def emit(self, record):
        topic = self.topic_map.get(record.levelname, 'debug_topic')
        log_dict = {k: getattr(record, k) for k in
                    ['message', 'levelname', 'name', 'filename', 'lineno', 'funcName', 'created']}
        self.kafka_producer.produce(topic, json.dumps(log_dict))


def get_logger(appConfig: ConfigModel):
    logger = logging.getLogger("xpose_logger")
    logger.setLevel(logging.DEBUG)

    if appConfig.log_to_console_enabled:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter(
            f'%(asctime)-25s | %(levelname)-8s | %(name)-15s | %(filename)-30s | %(funcName)-30s \n{"-"*26}» %(levelname)-8s | %(message)s\n'))
        logger.addHandler(ch)

    if appConfig.log_to_kafka_enabled:
        producer = Producer({'bootstrap.servers': appConfig.log_to_kafka_server_string})
        topic_map = {lvl: f"{lvl.lower()}_topic" for lvl in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']}
        kh = KafkaLoggingHandler(producer, topic_map)
        kh.setLevel(logging.DEBUG)
        kh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s::%(funcName)s] - %(message)s'))
        logger.addHandler(kh)
        logger.debug(f"Logger initialized: {logger.name}")

    return logger
