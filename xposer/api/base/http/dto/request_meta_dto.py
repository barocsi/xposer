#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from typing import Dict, Optional

from pydantic import BaseModel


class RequestMetaDTO(BaseModel):
    skip: Optional[int] = None
    limit: Optional[int] = None
    fields: Optional[Dict[str, int]] = None
