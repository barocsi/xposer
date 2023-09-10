from fastapi import APIRouter, Depends, FastAPI

from xposer.api.base.base_router import BaseRouter, Context
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http import SampleAppHTTP


class SampleSampleAppHTTPRouter(BaseRouter):
    api_prefix = 'api'

    def init_router(self, app: SampleAppHTTP):
        self.api = FastAPI()

        router = APIRouter()

        @router.get("/test/")
        def route1(ctx: Context = Depends(self.provide_context)):
            return {"router": "custom", "ctx": ctx.value}

        self.api.include_router(router=router, prefix=self.api_prefix)
