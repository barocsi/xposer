from logging import Logger

from xposer.models.configuration_model import ConfigModel


class Context:
    _instance = None
    logger: Logger = None
    config: ConfigModel = None
    state = None

    def __init__(self, logger, config, state):
        self.logger = logger
        self.config = config
        self.state = state
