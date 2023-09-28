from fastapi import APIRouter

from xposer.core.context import Context


class SampleAppHTTPService():
    @staticmethod
    def getRoute(ctx: Context):
        router = APIRouter()

        @router.get("/test/")
        async def sample_route():
            return {"router": "custom",
                    "xpcore": ctx.config.model_dump(),
                    "xpfacade": ctx.facade.config.model_dump(),
                    "xpapp": ctx.facade.app.config.model_dump()
                    }

        return router
