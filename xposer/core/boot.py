from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.facade_factory import FacadeFactory
from xposer.core.logger import get_logger


class Boot:

    @staticmethod
    def boot():
        config: ConfigModel = Configurator.buildConfig()
        logger = get_logger(config)
        config_json_str = config.model_dump_json(indent=4)
        logger.debug(f"Logger and configuration build completed. Configuration:\n{config_json_str}")
        context = Context(logger, config, {})
        facade = FacadeFactory.make(context)
        context.facade = facade
        facade.afterInititalization()
        logger.info(f"Boot sequence completed successfully. Facade {facade.name} started")
        return context
