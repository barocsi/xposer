#  Copyright (c) 2024. Aron Barocsi | All rights reserved.

import importlib
import json
from typing import cast

from xposer.core.abstract_xpcontroller import AbstractXPController
from xposer.core.context import Context


class XPControllerFactory:

    @staticmethod
    def make(ctx: Context) -> AbstractXPController:
        # Find and map slug to classnames
        xpcontroller_module_name = ctx.config.model_dump().get("xpcontroller_module_name", None)
        if xpcontroller_module_name is None:
            raise EnvironmentError(f"Unable to resolve xpcontroller module name from config")
        xpcontroller_class_name = ctx.config.model_dump().get("xpcontroller_class_name", None)
        if xpcontroller_class_name is None:
            raise EnvironmentError(f"Unable to resolve xpcontroller class name from config")

        # Instantiate the resolved class
        try:
            module = importlib.import_module(xpcontroller_module_name)
            class_ = getattr(module, xpcontroller_class_name)
            ctx.logger.debug(f"Trying to load module:{xpcontroller_module_name} class:{xpcontroller_class_name}")
            instance: AbstractXPController = cast(AbstractXPController, class_(ctx))
        except ImportError as e:
            raise ImportError(f"Module {xpcontroller_module_name} not found. Original error: {json.dumps(str(e))}")
        except AttributeError as e:
            raise AttributeError(f"Class {xpcontroller_class_name} not found in the module. Original error: {str(e)}")
        return instance
