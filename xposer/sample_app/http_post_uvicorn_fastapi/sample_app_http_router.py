from fastapi import APIRouter, FastAPI

from xposer.api.base.base_fastapi_router import BaseFastApiRouter


class SampleSampleAppHTTPRouter(BaseFastApiRouter):

    def start_router(self, api_prefix: str = "/api"):
        self.api = FastAPI()
        router = APIRouter()

        @router.get("/test/")
        def sample_route():
            return {"router": "custom",
                    "xpcore": self.ctx.config.model_dump(),
                    "xpfacade": self.ctx.facade.config.model_dump(),
                    "xpapp": self.ctx.facade.app.config.model_dump()
                    }

        self.api.include_router(router=router, prefix=api_prefix)
