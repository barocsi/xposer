import importlib
import json
from typing import cast

from xposer.core.abstract_facade import AbstractFacade
from xposer.core.context import Context


class FacadeFactory:

    @staticmethod
    def make(ctx: Context) -> AbstractFacade:
        # Find and map slug to classnames
        facade_module_name = ctx.config.model_dump().get("facade_module_name", None)
        if facade_module_name is None:
            raise EnvironmentError(f"Unable to resolve facade module name from config")
        facade_class_name = ctx.config.model_dump().get("facade_class_name", None)
        if facade_class_name is None:
            raise EnvironmentError(f"Unable to resolve facade class name from config")

        # Instantiate the resolved class
        try:
            module = importlib.import_module(facade_module_name)
            class_ = getattr(module, facade_class_name)
            ctx.logger.debug(f"Trying to load module:{facade_module_name} class:{facade_class_name}")
            instance: AbstractFacade = cast(AbstractFacade, class_(ctx))
        except ImportError as e:
            raise ImportError(f"Module {facade_module_name} not found. Original error: {json.dumps(str(e))}")
        except AttributeError as e:
            raise AttributeError(f"Class {facade_class_name} not found in the module. Original error: {str(e)}")
        return instance
