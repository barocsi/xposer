#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from typing import Any

from xposer.core.context import Context


class BaseService:
    app: Any = None

    def __init__(self, ctx: Context):
        self.ctx = ctx

    async def startService(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method to define their service")

    async def stopService(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method to define their service")
