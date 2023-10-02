import asyncio
import logging
import threading
import traceback
from asyncio import Event
from typing import Any, Callable, Optional, TypeVar, Union

import shortuuid

from xposer.core.context import Context

T = TypeVar('T', bound='MyClass')


class XPTask:

    @staticmethod
    async def cancel_tasks_for_loop(ctx, loop, timeout=1):
        pending = asyncio.all_tasks(loop=loop)

        for task in pending:
            task.cancel()

        try:
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout)
        except asyncio.TimeoutError:
            ctx.logger.warn(f"Tasks did not cancel within {timeout} seconds.")
        except asyncio.CancelledError:
            ctx.logger.warn("Task was cancelled, this is expected behavior.")
        finally:
            await loop.shutdown_asyncgens()

        # Recheck for remaining tasks
        remaining = asyncio.all_tasks(loop=loop)

        if remaining:
            ctx.logger.warn(f"{len(remaining)} tasks have not terminated yet.")
        for task in remaining:
            ctx.logger.warn(f"Unterminated task name: {task.get_name()}")
        else:
            ctx.logger.warn("All tasks have been canceled.")

        # Safely close the loop
        if loop.is_running():
            ctx.logger.warn("Loop is still running. Can't close it now.")
        else:
            loop.close()

    def __init__(self, ctx: Context) -> None:
        self.re_raise_exception: Optional[bool] = None
        self.wrapped_threaded_func_task: Optional[asyncio.Task] = None
        self.wrapped_threaded_func_task_slug: Optional[str] = None
        self.wrapped_threaded_func_task_loop: Optional[asyncio.AbstractEventLoop] = None
        self.custom_logger: Optional[logging.Logger] = None
        self.shutdown_event: Event = None
        self.id = shortuuid.ShortUUID().random(length=7)
        task: Optional[asyncio.Task]
        ctx: Context
        task_loop: Optional[asyncio.AbstractEventLoop]
        is_shut_down: bool = False
        self.ctx = ctx

    @property
    def logger(self) -> logging.Logger:
        return self.custom_logger or logging.getLogger(self.wrapped_threaded_func_task_slug or "XPTask")

    def handle_task_loop_exception(self, loop: asyncio.AbstractEventLoop, context: dict) -> None:
        self.logger.error(f"[XPTask] Caught exception in {self.wrapped_threaded_func_task_slug}: {context['message']}")
        exception = context.get('exception')
        if self.ctx.exception_queue:
            self.ctx.exception_queue.put_nowait(exception)

    def run_loop_in_thread(self, to_be_threadified_func: Callable) -> None:
        async def coroutine_wrapper():
            await to_be_threadified_func()

        self.wrapped_threaded_func_task_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.wrapped_threaded_func_task_loop)
        self.wrapped_threaded_func_task_loop.set_exception_handler(self.handle_task_loop_exception)
        self.wrapped_threaded_func_task = self.wrapped_threaded_func_task_loop.create_task(coroutine_wrapper())
        self.wrapped_threaded_func_task.set_name("XPTASK:WrappedThreadedFunctionCoroutine")
        self.wrapped_threaded_func_task_loop.run_forever()

    def thread_exception_handler(args):
        print("Exception in thread:", args['thread'].name)
        traceback.print_exception(args['exc_type'], args['exc_value'], args['traceback'])

    threading.excepthook = thread_exception_handler

    def create_task(self,
                    to_be_threadified_func: Callable,
                    exception_callback: Callable[[Union[Any, None], Exception], None],
                    custom_logger: Optional[logging.Logger] = None,
                    task_slug: str = '',
                    re_raise_exception: bool = True) -> T:
        self.on_exception_callback = exception_callback
        self.custom_logger = custom_logger
        self.re_raise_exception = re_raise_exception
        self.wrapped_threaded_func_task_slug = task_slug
        self.logger.debug("Creating task in a new thread")
        self.thread = threading.Thread(target=self.run_loop_in_thread, args=(to_be_threadified_func,))
        self.thread.daemon = True
        self.thread.start()
        return self

    async def shutdown(self):
        # Todo implement graceful options for XPTasks that are not actually daemons
        self.ctx.logger.debug(f"Shutting down XPtask:{self.id}")

        await XPTask.cancel_tasks_for_loop(self.ctx, self.wrapped_threaded_func_task_loop)
        """
        if self.thread.is_alive():
            self.ctx.logger.warning(f"Terminating thread for XPtask:{self.id}")
        self.thread.join()
        pass
        """
        ...

    def __del__(self) -> None:
        """Close the event loop if it is not already closed."""
        self.shutdown()
