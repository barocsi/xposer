from typing import Any

from fastapi import APIRouter

from xposer.core.context import Context


class BaseRouter:
    app: Any = None

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def start_router(self, *args, **kwargs) -> APIRouter:
        raise NotImplementedError("Subclasses must implement this method to define their router")

    def stop_router(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method to define their router")
