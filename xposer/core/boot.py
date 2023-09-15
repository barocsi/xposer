import asyncio
import json
import signal

from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.facade_factory import FacadeFactory
from xposer.core.logger import get_logger


class Boot:
    ctx: Context = None

    async def shutdown(self):
        self.ctx.logger.info(f"Shutting down application")
        self.ctx.facade.tearDown()
        await asyncio.sleep(1)
        self.ctx.logger.info(f"Shutting down completed")

    def _sync_shutdown_handler(self,a,b):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.shutdown())


    def boot(self):
        # Config management
        config: ConfigModel = Configurator.buildConfig()

        # Logger management
        logger = get_logger(config)

        # Context setup
        context = Context(logger, config, {})
        self.ctx = context

        # Create a facade
        facade = FacadeFactory.make(context)
        context.facade = facade

        # Add graceful shutdown feature
        # Signal handling setup
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, self._sync_shutdown_handler)

        # Optional hooking
        facade.afterInititalization()

        # Verbose
        logger.info(f"Boot sequence completed successfully. Facade {facade.name} started")
        logger.debug(f"List of loaded configurations:")
        logger.debug(f"Application level:")
        logger.debug(json.dumps(context.config.model_dump()))
        return context
