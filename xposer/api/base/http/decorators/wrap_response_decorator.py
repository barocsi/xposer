from functools import wraps
from typing import Callable

from fastapi import HTTPException

from xposer.api.base.http.dto.response_wrapper_dto import ResponseWrapperDTO


def ResponseWrapperDecorator(ctx):
    def actual_decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return ResponseWrapperDTO(result="success", data=result)
            except Exception as e:
                ctx.logger.error(f"FastAPI Internal error occurred: {e}")  # Logging the error
                detail = ResponseWrapperDTO(result="error", exception=str(e)).model_dump()
                raise HTTPException(status_code=500, detail=detail)

        return wrapper

    return actual_decorator
