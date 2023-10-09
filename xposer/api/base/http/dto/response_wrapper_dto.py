from typing import Any

from pydantic import BaseModel


class ResponseWrapperDTO(BaseModel):
    result: str
    exception: Any = None
    data: Any = None