import asyncio
import logging
import threading
import queue
import typing
from functools import partial
from typing import Any, Callable, Optional, Type
import sys

from xposer.core.context import Context


class XPTask:
    task: asyncio.Task
    ctx: Context
    task_loop:asyncio.AbstractEventLoop

    def __init__(self, ctx: Context):
        self.re_raise_exception: Optional[bool] = None
        self.task: Optional[asyncio.Task] = None
        self.task_slug: Optional[str] = None
        self.task_loop: Optional[asyncio.AbstractEventLoop] = None
        self.custom_logger: Optional[logging.Logger] = None
        self.exception_queue = queue.Queue()
        self.ctx = ctx

    @property
    def logger(self) -> logging.Logger:
        return self.custom_logger or logging.getLogger(self.task_slug or "XPTask")

    def handle_task_loop_exception(self, loop, context):
        self.logger.error(f"Caught exception in {self.task_slug}: {context['message']}")
        exception = context.get('exception')
        if self.ctx.exception_queue:
            self.ctx.exception_queue.put(exception)

    def run_loop_in_thread(self, unpacked_partial_func):
        self.task_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.task_loop)
        self.task_loop.set_exception_handler(self.handle_task_loop_exception)
        self.task = self.task_loop.create_task(unpacked_partial_func)
        self.task_loop.run_until_complete(self.task)

    def create_task(self,
                    to_be_coroutinified_partial_func: partial,
                    exception_callback: Callable[[typing.Union[Any, None], Exception], None],
                    custom_logger: Optional[logging.Logger] = None,
                    task_slug: str = '',
                    re_raise_exception: bool = True) -> asyncio.Task:

        if not isinstance(to_be_coroutinified_partial_func, partial):
            raise TypeError("coroutine_func must be a functools.partial object")

        self.on_exception_callback = exception_callback
        self.custom_logger = custom_logger
        self.re_raise_exception = re_raise_exception
        self.task_slug = task_slug

        unpacked_partial_func = to_be_coroutinified_partial_func()
        self.logger.error(f"Creating task in a new thread")
        thread = threading.Thread(target=self.run_loop_in_thread, args=(unpacked_partial_func,))
        thread.start()
        thread.join()
        # On the main loop, start monitor the exceptions from child threads queue
        return self.task

    def __del__(self):
        if self.task_loop and not self.task_loop.is_closed():
            self.task_loop.close()
