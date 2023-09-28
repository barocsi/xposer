import asyncio
import queue
import signal
from functools import partial
from typing import Any

from xposer.api.base.xpose_task import XPTask
from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.facade_factory import FacadeFactory
from xposer.core.logger import get_logger


class Boot:
    """Boot sequence class to manage the application initialization and shutdown.

    Steps in boot sequence:
    1. Load configuration and other contextual parameters.
    2. Instantiate the facade.
    3. Create an XPTask to manage threaded asynchronous services.
    4. Handle exceptions through a thread-safe queue.
    5. Process parallel tasks, monitoring, and shutdown requests.
    """

    def __init__(self) -> None:
        self.ctx: Context = None
        self.shutdown_event: asyncio.Event = asyncio.Event()

    async def shutdown(self) -> None:
        """Perform application shutdown."""
        self.ctx.logger.info("Shutting down application")
        await self.ctx.facade.tearDownApp()
        await asyncio.sleep(1)
        self.ctx.logger.info("Shutting down completed")
        self.shutdown_event.set()

    def _sync_shutdown_handler(self, a: Any, b: Any) -> None:
        """Sync shutdown handler."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.shutdown())

    async def monitor_exceptions(self) -> None:
        """Monitor for exceptions from the exception queue."""
        while True:
            try:
                exception = self.ctx.exception_queue.get_nowait()
                self.ctx.logger.error(f"Raising exception from boot monitor_exceptions {exception}")
                raise exception
            except queue.Empty:
                await asyncio.sleep(1)

    def handle_loop_exceptions(self, loop: asyncio.AbstractEventLoop, context: dict) -> None:
        """Handle exceptions in the event loop."""
        task = context.get('future')
        if task:
            exception = task.exception()
            if exception:
                self.ctx.logger.error(f"Main Boot thread caught loop exception: {exception}")
                loop.stop()
                raise exception

    async def boot(self) -> Context:
        """Boot sequence for initializing and running the application."""

        # Configuration management
        config: ConfigModel = Configurator.buildConfig()

        # Logger setup
        logger = get_logger(config)

        # Context setup
        context = Context(logger, config, {})
        self.ctx = context

        # Facade creation
        facade = FacadeFactory.make(context)
        await facade.asyncInit()

        # Run services asynchronously
        XPTask(self.ctx).create_task(
            to_be_threadified_func=facade.startFacadeServices,
            exception_callback=None,
            custom_logger=logger,
            task_slug='boot_facade_startFacadeServices',
            re_raise_exception=True
        )

        context.facade = facade

        # Graceful shutdown setup
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, self._sync_shutdown_handler)

        # Global exception handling
        asyncio.get_event_loop().set_exception_handler(self.handle_loop_exceptions)

        # Logging
        logger.info(f"Boot sequence completed successfully. Facade {facade.name} started")

        try:
            await asyncio.gather(self.monitor_exceptions(), self.shutdown_event.wait(), return_exceptions=False)
        except Exception as e:
            self.ctx.logger.error(f"Caught exception: {e}")
            await self.shutdown()
            raise e

        return context
