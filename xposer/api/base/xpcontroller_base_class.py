#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from abc import ABC
from typing import List

from pydantic import BaseModel

from xposer.api.base.base_service import BaseService
from xposer.core.abstract_xpcontroller import AbstractXPController
from xposer.core.context import Context


class XPControllerBaseClass(AbstractXPController, ABC):
    name: str = "XPControllerBaseClass"
    config_prefix: str = "xpcontroller_"  # Class level

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.config = self.mergeConfigurationFromPrefix()
        # TODO self.socket_router: Any = None
        self.xpcontroller_conf_class: BaseModel
        self.services: List[BaseService] = []

    def mergeConfigurationFromPrefix(self) -> BaseModel:
        return BaseModel.model_construct()

    async def startXPController(self):
        raise NotImplementedError

    async def tearDownXPController(self):
        raise NotImplementedError

    async def asyncInit(self):
        ...
