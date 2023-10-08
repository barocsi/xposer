from functools import wraps
from typing import Callable

from fastapi import HTTPException

from cellx.lib.models.dto.response_wrapper_dto import ResponseWrapperDTO


def ResponseWrapperDecorator(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        meta = {}
        try:
            result = await func(*args, **kwargs)
            meta['total_count'] = 1  # Replace with actual count if available
            meta['has_more'] = False  # Replace with actual value if available
            return ResponseWrapperDTO(result="success", data=result, meta=meta)
        except Exception as e:
            detail = ResponseWrapperDTO(result="error", exception=str(e), meta=meta).model_dump()
            raise HTTPException(status_code=500, detail=detail)

    return wrapper
