from typing import Dict, List, Optional

from pydantic import BaseModel


class RequestMetaDTO(BaseModel):
    skip: Optional[int] = None
    limit: Optional[int] = None
    fields: Optional[Dict[str,int]] = None