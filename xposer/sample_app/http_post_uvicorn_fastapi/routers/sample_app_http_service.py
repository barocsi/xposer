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
                    "xpcontroller": ctx.xpcontroller.config.model_dump()
                    }

        return router
