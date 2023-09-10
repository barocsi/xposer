from typing import Any, List, TypedDict
from fastapi import FastAPI, APIRouter

from xposer.core.context import Context


class BaseRouter:
    app: Any = None

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def init_router(self, *args, **kwargs) -> APIRouter:
        raise NotImplementedError("Subclasses must implement this method to define their router")
