import queue
from logging import Logger

from xposer.core.configuration_model import ConfigModel


class Context:
    _instance = None
    logger: Logger = None
    config: ConfigModel = None
    message_queue = queue.Queue()
    exception_queue = queue.Queue()
    state = None
    facade: None

    def __init__(self, logger, config, state):
        self.logger = logger
        self.config = config
        self.state = state
