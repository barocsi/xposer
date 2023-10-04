import asyncio
import queue
import signal
import sys
import threading
import traceback
from typing import Any

from xposer.core.completed_exception import CompletedException
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
        self.ctx.logger.warning("\n*** CLI/Sync Shutdown signal received ***")
        if not self.shutdown_in_progress:
            try:
                asyncio.get_running_loop()
                asyncio.create_task(self.shutdown())
            except RuntimeError:
                sys.exit()

    def thread_exception_handler(self, args):
        try:
            thread_name = args.thread.name if args.thread else "Unknown"
            self.ctx.logger.error(f"Exception in thread: {thread_name}")
            tb = args.exc_value.__traceback__
            traceback.print_exception(args.exc_type, args.exc_value, tb)
            if threading.current_thread().name == "MainThread":
                self._sync_shutdown_handler()
            else:
                if self.ctx.exception_queue:
                    self.ctx.exception_queue.put_nowait(args)
                else:
                    sys.exit(0)
        except Exception as e:
            print(f"Failed to handle exception in thread: {e}")

    async def shutdown(self) -> None:
        if self.shutdown_in_progress:
            return
        self.ctx.logger.warning("*** Internal Shutdown signal received ***")
        self.shutdown_in_progress = True
        self.ctx.logger.info("Shutting down application initiated")
        self.ctx.message_queue.put({'target': None, 'message': 'shutdown'})
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
                if isinstance(exception, CompletedException):
                    self.ctx.logger.info(f"Controller completed: {exception.args[0]}")
                else:
                    self.ctx.logger.error(f"Exception: {exception}")
                await self.shutdown()
            except (queue.Empty, asyncio.CancelledError):
                ...
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
        loop = asyncio.get_event_loop()
        loop.id = "main_loop"
        xpcontroller = XPControllerFactory.make(context)
        await xpcontroller.asyncInit()
        asyncio.get_event_loop().set_exception_handler(self.handle_loop_exceptions)
        threading.excepthook = self.thread_exception_handler
        xptask_initialization_future = asyncio.Future()
        xptask = XPTask(self.ctx)

        def initialization_callback():
            loop.call_soon_threadsafe(xptask_initialization_future.set_result, None)

        logger.info(f"Boot sequence completed. Starting XPController {xpcontroller.name}")
        xptask.startup(
            to_be_threadified_func=xpcontroller.startXPController,
            initialization_callback=initialization_callback,
            teardown_func=xpcontroller.tearDownXPController,
            main_event_loop=loop,
            exception_callback=None,
            custom_logger=logger,
            task_slug='boot_xpcontroller_startXPController',
            re_raise_exception=True
        )
        await xptask_initialization_future
        self.ctx.xptask_list.append(xptask)
        context.xpcontroller = xpcontroller

        for s in (signal.SIGTERM, signal.SIGINT):
            signal.signal(s, self._sync_shutdown_handler)

        logger.info(f"XPController {xpcontroller.name} sync process complete. Async tasks might be in progress.")

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
