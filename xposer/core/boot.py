import asyncio
import queue
import signal
import sys
from typing import Any

from xposer.api.base.xpose_task import XPTask
from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.logger import get_logger
from xposer.core.xpcontroller_factory import XPControllerFactory


class Boot:
    """Boot sequence class to manage the application initialization and shutdown.

    Steps in boot sequence:
    1. Load configuration and other contextual parameters.
    2. Instantiate the xpcontroller.
    3. Create an XPTask to manage threaded asynchronous services.
    4. Handle exceptions through a thread-safe queue.
    5. Process parallel tasks, monitoring, and shutdown requests.
    """

    def __init__(self) -> None:
        self.ctx: Context = None
        self.shutdown_event: asyncio.Event = asyncio.Event()
        self.shutdown_in_progress: bool = False

    def _sync_shutdown_handler(self, a: Any, b: Any) -> None:
        """Sync shutdown handler."""
        if self.shutdown_in_progress is True:
            pass
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.shutdown())

    async def shutdown(self) -> None:
        """Perform application shutdown."""
        if self.shutdown_in_progress is True:
            pass
        self.shutdown_in_progress = True
        self.ctx.logger.info("Shutting down application")
        self.ctx.message_queue.put({'target': None, 'message': 'shutdown'})
        await self.ctx.xpcontroller.tearDownXPController()
        await asyncio.sleep(1)

        # Shutdown XPTasks
        await asyncio.gather(*(xptask.shutdown() for xptask in self.ctx.xptask_list))
        # Shutdown loop tasks
        await XPTask.cancel_tasks_for_loop(asyncio.get_event_loop())
        sys.exit()

    async def monitor_exceptions(self) -> None:
        while True:
            try:
                if self.shutdown_event is not None and self.shutdown_event.is_set():
                    break
                exception = self.ctx.exception_queue.get_nowait()
                self.ctx.logger.error(f"Raising exception from boot monitor_exceptions {exception}")
                await self.shutdown()
            except queue.Empty:
                await asyncio.sleep(0.1)

    def handle_loop_exceptions(self, loop: asyncio.AbstractEventLoop, context: dict) -> None:
        """Handle exceptions in the event loop."""
        task = context.get('future')
        if task:
            exception = task.exception()
            if exception:
                self.ctx.logger.error(f"Main Boot thread caught loop exception: {exception}")
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.shutdown())

    async def boot(self) -> Context:
        """Boot sequence for initializing and running the application."""

        # Configuration management
        config: ConfigModel = Configurator.buildConfig()

        # Logger setup
        logger = get_logger(config)

        # Context setup
        context = Context(logger, config, {})
        self.ctx = context

        # XPController creation
        xpcontroller = XPControllerFactory.make(context)
        await xpcontroller.asyncInit()

        # Global exception handling
        asyncio.get_event_loop().set_exception_handler(self.handle_loop_exceptions)

        # For debugging
        main_loop = asyncio.get_event_loop()
        main_loop.id = "main_loop"
        # Run services asynchronously
        xptask = XPTask(self.ctx).create_task(
            to_be_threadified_func=xpcontroller.startXPControllerServices,
            exception_callback=None,
            custom_logger=logger,
            task_slug='boot_xpcontroller_startXPControllerServices',
            re_raise_exception=True
        )
        self.ctx.xptask_list.append(xptask)
        context.xpcontroller = xpcontroller

        # Graceful shutdown setup
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, self._sync_shutdown_handler)

        # Logging
        logger.info(f"Boot sequence completed successfully. XPController {xpcontroller.name} started")

        try:
            await asyncio.gather(self.monitor_exceptions(),
                                 self.shutdown_event.wait(),
                                 return_exceptions=False)
        except Exception as e:
            self.ctx.logger.error(f"[Boot] Caught exception: {e}")
            await self.shutdown()
            raise e

        return context
