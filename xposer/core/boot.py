import asyncio
import queue
import signal
import sys
from typing import Any

from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.logger import get_logger
from xposer.core.xpcontroller_factory import XPControllerFactory
from xposer.core.xpose_task import XPTask


class Boot:
    def __init__(self) -> None:
        self.ctx = None  # type: Context
        self.shutdown_event = asyncio.Event()
        self.shutdown_in_progress = False

    def _sync_shutdown_handler(self, *_: Any) -> None:
        self.ctx.logger.warning("\n*** CLI Shutdown signal received ***")
        if not self.shutdown_in_progress:
            asyncio.create_task(self.shutdown() )

    async def shutdown(self) -> None:
        if self.shutdown_in_progress:
            return
        self.ctx.logger.warning("*** Internal Shutdown signal received ***")
        self.shutdown_in_progress = True
        self.ctx.logger.info("Shutting down application initiated")
        self.ctx.message_queue.put({'target': None, 'message': 'shutdown'})
        await self.ctx.xpcontroller.tearDownXPController()
        await asyncio.sleep(1)

        tasks = [asyncio.create_task(xptask.shutdown()) for xptask in self.ctx.xptask_list]
        self.ctx.logger.debug(f"Shutting down XPTasks")
        await asyncio.gather(*tasks)
        self.ctx.logger.debug(f"Shutting down Main loop")
        await XPTask.cancel_tasks_for_loop(self.ctx, asyncio.get_event_loop())
        self.ctx.logger.debug(f"Main shutdown sequence completed")
        sys.exit()

    async def monitor_exceptions(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                exception = self.ctx.exception_queue.get_nowait()
                self.ctx.logger.error(f"Exception: {exception}")
                await self.shutdown()
            except (queue.Empty, asyncio.CancelledError):
                await asyncio.sleep(0.1)

    def handle_loop_exceptions(self, loop: asyncio.AbstractEventLoop, context: dict) -> None:
        task = context.get('future')
        if task and (exc := task.exception()):
            if isinstance(exc, asyncio.CancelledError) and self.shutdown_in_progress:
                return  # Skip logging and shutdown for CancelledError when shutdown is in progress

            self.ctx.logger.error(f"Loop exception: {exc}")

            if not self.shutdown_in_progress:
                loop.run_until_complete(self.shutdown())

    async def boot(self) -> Context:
        config = Configurator.buildConfig()
        logger = get_logger(config)
        context = Context(logger, config, {})
        self.ctx = context
        xpcontroller = XPControllerFactory.make(context)
        await xpcontroller.asyncInit()

        asyncio.get_event_loop().set_exception_handler(self.handle_loop_exceptions)

        xptask = XPTask(self.ctx).create_task(
            xpcontroller.startXPControllerServices,
            None,
            logger,
            'boot_xpcontroller_startXPControllerServices',
            True
        )
        self.ctx.xptask_list.append(xptask)
        context.xpcontroller = xpcontroller

        for s in (signal.SIGTERM, signal.SIGINT):
            signal.signal(s, self._sync_shutdown_handler)

        logger.info(f"Boot sequence completed. XPController {xpcontroller.name} started")

        try:
            monitor_task = asyncio.create_task(self.monitor_exceptions())
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            await asyncio.gather(monitor_task, shutdown_task)
        except asyncio.CancelledError as ce:
            if self.shutdown_in_progress:
                self.ctx.logger.debug("CancelledError caught during shutdown. This is expected.")
            else:
                self.ctx.logger.error(f"Exception: {ce}")
                await self.shutdown()
                raise ce
        except Exception as e:
            self.ctx.logger.error(f"Exception: {e}")
            if not self.shutdown_in_progress:
                await self.shutdown()
            raise e

        return context
