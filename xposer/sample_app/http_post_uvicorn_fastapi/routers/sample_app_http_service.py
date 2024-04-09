#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from xposer.api.base.http.decorators.wrap_response_decorator import ResponseWrapperDecorator
from xposer.core.context import Context


class SampleModel(BaseModel):
    name: str
    age: int


class SampleAppHTTPService:
    @staticmethod
    def getRoute(ctx: Context):
        router = APIRouter()

        @router.get("/test/")
        @ResponseWrapperDecorator(ctx)
        async def sample_route():
            return {
                "router": "custom",
                "xpcore": ctx.config.model_dump(),
                "xpcontroller": ctx.xpcontroller.config.model_dump()
                }

        @router.get("/test/exception")
        @ResponseWrapperDecorator(ctx)
        async def sample_route_with_exception():
            raise Exception("Test Exception")

        @router.get("/test/validation_error")
        @ResponseWrapperDecorator(ctx)
        async def sample_route_with_validation_error():
            data = {"name": "Alice", "age": "not_an_int"}  # Invalid data
            try:
                # This will raise a ValidationError
                valid_data = SampleModel.parse_obj(data)
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))

            return valid_data

        return router
