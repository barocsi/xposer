#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class BaseFastApiRouterConfigModel(BaseSettings):
    model_config = ConfigDict(extra='allow')
