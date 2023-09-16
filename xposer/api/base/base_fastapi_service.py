from typing import List

import uvicorn
from fastapi import APIRouter, FastAPI

from xposer.api.base.base_service import BaseService


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

        config = uvicorn.Config(app=self.fastApi, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
