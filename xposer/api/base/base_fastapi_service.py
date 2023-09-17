import logging
from typing import List

import uvicorn
from fastapi import APIRouter, FastAPI
from uvicorn.config import LOGGING_CONFIG

from xposer.api.base.base_service import BaseService

LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.error"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["xpose_logger"] = {
    "handlers": ["default"],
    "level": "DEBUG",
}


class Context:
    def __init__(self, value: str):
        self.value = value


class BaseFastApiService(BaseService):
    fastApi: FastAPI = None

    def provide_context(self) -> Context:
        return self.ctx

    async def startService(self,
                           host,
                           port,
                           routes: List[APIRouter],
                           api_prefix: str = "/api",
                           callback=None):
        self.fastApi = FastAPI()
        for route in routes:
            self.fastApi.include_router(route, prefix=api_prefix)

        @self.fastApi.on_event("startup")
        async def on_startup():
            if callback:
                callback(None)

        xpose_logger = self.ctx.logger

        for uvicorn_logger_name in ["uvicorn", "uvicorn.error"]:
            uvicorn_specific_logger = logging.getLogger(uvicorn_logger_name)
            uvicorn_specific_logger.handlers = xpose_logger.handlers
            uvicorn_specific_logger.propagate = False

        config = uvicorn.Config(app=self.fastApi,
                                host=host,
                                port=port,
                                log_level="info",
                                log_config=None
                                )
        server = uvicorn.Server(config)
        await server.serve()
