import asyncio
import logging
import queue
import threading
from typing import Any, Callable, Optional, Union

from xposer.core.context import Context


class XPTask:
    """XPTask class for wrapping potentially long-running functions in separate async threads.

    The class manages exceptions through a thread-safe queue mechanism.

    Attributes:
        task (asyncio.Task): The asyncio task wrapped by XPTask.
        ctx (Context): Application context.
        task_loop (asyncio.AbstractEventLoop): Event loop for the task.
    """

    task: Optional[asyncio.Task]
    ctx: Context
    task_loop: Optional[asyncio.AbstractEventLoop]

    def __init__(self, ctx: Context) -> None:
        """Initialize the XPTask with the given application context.

        Args:
            ctx (Context): Application context.
        """
        self.re_raise_exception: Optional[bool] = None
        self.task: Optional[asyncio.Task] = None
        self.task_slug: Optional[str] = None
        self.task_loop: Optional[asyncio.AbstractEventLoop] = None
        self.custom_logger: Optional[logging.Logger] = None
        self.exception_queue = queue.Queue()
        self.ctx = ctx

    @property
    def logger(self) -> logging.Logger:
        """Get the logger for the task.

        Returns:
            logging.Logger: Logger object.
        """
        return self.custom_logger or logging.getLogger(self.task_slug or "XPTask")

    def handle_task_loop_exception(self, loop: asyncio.AbstractEventLoop, context: dict) -> None:
        """Handle exceptions in the task loop."""
        self.logger.error(f"Caught exception in {self.task_slug}: {context['message']}")
        exception = context.get('exception')
        # Thread safe method of raising exceptions
        if self.ctx.exception_queue:
            self.ctx.exception_queue.put(exception)

    def run_loop_in_thread(self, to_be_threadified_func: Callable) -> None:
        """Run the event loop for the task in a separate thread."""

        async def coroutine_wrapper():
            await to_be_threadified_func()

        self.task_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.task_loop)
        self.task_loop.set_exception_handler(self.handle_task_loop_exception)
        self.task = self.task_loop.create_task(coroutine_wrapper())
        self.task_loop.run_until_complete(self.task)

    def create_task(self,
                    to_be_threadified_func: Callable,
                    exception_callback: Callable[[Union[Any, None], Exception], None],
                    custom_logger: Optional[logging.Logger] = None,
                    task_slug: str = '',
                    re_raise_exception: bool = True) -> asyncio.Task:
        self.on_exception_callback = exception_callback
        self.custom_logger = custom_logger
        self.re_raise_exception = re_raise_exception
        self.task_slug = task_slug
        self.logger.debug("Creating task in a new thread")
        thread = threading.Thread(target=self.run_loop_in_thread, args=(to_be_threadified_func,))
        thread.start()
        return self.task

    def __del__(self) -> None:
        """Close the event loop if it is not already closed."""
        if self.task_loop and not self.task_loop.is_closed():
            self.task_loop.close()
