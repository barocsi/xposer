from fastapi import APIRouter, FastAPI

from xposer.api.base.base_fastapi_router import BaseFastApiRouter
from xposer.sample_app.http_post_uvicorn_fastapi.sample_app_http import SampleAppHTTP


class SampleSampleAppHTTPRouter(BaseFastApiRouter):

    def init_router(self, app: SampleAppHTTP, api_prefix: str = "/api"):
        self.api = FastAPI()
        router = APIRouter()

        @router.get("/test/")
        def sample_route():
            return {"router": "custom", "somevariable": self.ctx.config.highlevel_variable}

        self.api.include_router(router=router, prefix=api_prefix)
