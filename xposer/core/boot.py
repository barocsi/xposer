import asyncio
import signal

from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.facade_factory import FacadeFactory
from xposer.core.logger import get_logger

class Boot:
    def __init__(self):
        self.ctx: Context = None
        self.shutdown_event = asyncio.Event()  # Shutdown event

    async def shutdown(self):
        self.ctx.logger.info(f"Shutting down application")
        self.ctx.facade.tearDown()
        await asyncio.sleep(1)
        self.ctx.logger.info(f"Shutting down completed")
        self.shutdown_event.set()  # Set the shutdown event

    def _sync_shutdown_handler(self, a, b):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.shutdown())

    async def boot(self):
        # Config management
        config: ConfigModel = Configurator.buildConfig()

        # Logger management
        logger = get_logger(config)

        # Context setup
        context = Context(logger, config, {})
        self.ctx = context

        # Create a facade
        facade = FacadeFactory.make(context)
        await facade.asyncInit()
        asyncio.create_task(facade.startServices())
        context.facade = facade

        # Add graceful shutdown feature
        # Signal handling setup
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, self._sync_shutdown_handler)

        # Verbose
        logger.info(f"Boot sequence completed successfully. Facade {facade.name} started")
        logger.debug(f"List of loaded configurations:")
        logger.debug(f"Facade level:")
        logger.debug(context.facade.config.model_dump_json(indent=4))
        logger.debug(f"Application level:")
        logger.debug(context.facade.app.config.model_dump_json(indent=4))

        # Wait for the shutdown event to be set
        await self.shutdown_event.wait()

        return context
