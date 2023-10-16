import asyncio
import logging
import traceback
from typing import List

import uvicorn
from fastapi import APIRouter, FastAPI
from starlette.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

from xposer.api.base.base_service import BaseService
from xposer.api.base.http.dto.response_wrapper_dto import ResponseWrapperDTO
from xposer.api.base.http.routes.debug_routes import XPDebugRouter
from xposer.core.context import Context

LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.error"]["handlers"] = ["default"]
LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] = "ERROR"
LOGGING_CONFIG["loggers"]["xpose_logger"] = {
    "handlers": ["default"],
    "level": "DEBUG",
    }


class BaseFastApiService(BaseService):
    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.fastApi: FastAPI = None

    async def startService(
            self,
            host,
            port,
            routes: List[APIRouter],
            api_prefix: str = "/api",
            callback=None
            ):
        self.fastApi = FastAPI(tail_slash=True)

        @self.fastApi.exception_handler(Exception)
        async def http_exception_handler(request, e):
            backtrace_info = traceback.format_exc()  # Gets the traceback information
            self.ctx.logger.error(
                f"FastAPI Internal error occurred @self.fastApi.exception_handler: {e}\n{backtrace_info}"
                )  # Logging the error with traceback
            detail = ResponseWrapperDTO(result="error", exception=str(e)).model_dump()
            return JSONResponse(status_code=500, content=detail)

        for route in routes:
            self.fastApi.include_router(route, prefix=api_prefix)

        if self.ctx.config.debug_enabled_for_built_in_http:
            debug_routes = [XPDebugRouter().getRoute(self.ctx)]
            for route in debug_routes:
                self.fastApi.include_router(route, prefix=api_prefix)

        @self.fastApi.on_event("startup")
        async def on_startup():
            if callback:
                self.ctx.logger.debug("FastAPI initialization successful")
                callback(None)

        xpose_logger = self.ctx.logger

        for uvicorn_logger_name in ["uvicorn", "uvicorn.error"]:
            uvicorn_specific_logger = logging.getLogger(uvicorn_logger_name)

            # Set log level for uvicorn.error specifically
            if uvicorn_logger_name == "uvicorn.error":
                uvicorn_specific_logger.setLevel(logging.INFO)

            uvicorn_specific_logger.handlers = xpose_logger.handlers
            uvicorn_specific_logger.propagate = False

        config = uvicorn.Config(
            app=self.fastApi,
            host=host,
            port=port,
            forwarded_allow_ips="*",
            log_level="debug",
            log_config=None
            )
        server = uvicorn.Server(config)
        server_task = asyncio.create_task(server.serve())
        server_task.set_name("Fastapi::Service")
        return server
