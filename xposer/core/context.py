#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

import queue
from logging import Logger
from typing import Any, Dict, List

from xposer.core.configuration_model import ConfigModel


class Context:
    _instance = None
    logger: Logger = None
    config: ConfigModel = None
    message_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
    exception_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
    xptask_list: List[Any] = []
    state = None
    xpcontroller: None

    def __init__(self, logger, config, state):
        self.logger = logger
        self.config = config
        self.state = state
