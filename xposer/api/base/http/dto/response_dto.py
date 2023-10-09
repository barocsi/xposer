from typing import Any, Optional

from pydantic import BaseModel


class ResponseStatsDTO(BaseModel):
    total_count: int = None
    has_mode: Optional[bool] = None


class ResponseDTO(BaseModel):
    items: Any = None
    stats: Optional[ResponseStatsDTO] = None
