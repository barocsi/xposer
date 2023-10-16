import traceback
from functools import wraps

from fastapi import HTTPException

from xposer.api.base.http.dto.response_wrapper_dto import ResponseWrapperDTO


def ResponseWrapperDecorator(ctx):
    def actual_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return ResponseWrapperDTO(result="success", data=result)
            except Exception as e:
                backtrace_info = traceback.format_exc()  # Gets the traceback information
                ctx.logger.error(
                    f"FastAPI Internal error occurred @ResponseWrapperDecorator: {e}\n{backtrace_info}"
                    )  # Logging the error with traceback
                detail = ResponseWrapperDTO(result="error", exception=str(e)).model_dump()
                raise HTTPException(status_code=500, detail=detail)

        return wrapper

    return actual_decorator
