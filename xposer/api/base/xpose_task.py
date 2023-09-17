import asyncio
import logging
from typing import Any, Callable, Optional, Coroutine


class XPTask:
    """
    XPTask is a coroutine wrapper designed to wrap long-running subcoroutines.
    It facilitates catching exceptions in a concise, compact, and boilerplate-free fashion.
    """

    def __init__(self):
        self.re_raise_exception: Optional[bool] = None
        self.task: Optional[asyncio.Task] = None
        self.task_slug: Optional[str] = None
        self.custom_logger: Optional[logging.Logger] = None
        self.on_exception_callback: Optional[Callable[[Any, Exception], None]] = None

    @property
    def logger(self) -> logging.Logger:
        """
        :return: Custom logger if available, otherwise a logger based on the task slug.
        """
        return self.custom_logger or logging.getLogger(self.task_slug or "XPTask")

    async def wrapped_coro(self, coroutine: Coroutine) -> None:
        """
        A coroutine wrapper that catches exceptions and optionally re-raises them.

        :param coroutine: The original coroutine to be wrapped.
        :raises Exception: If re_raise_exception is True, the caught exception is re-raised.
        """
        try:
            await coroutine
        except Exception as e:
            self.logger.error(f"Caught exception in {self.task_slug}: {e}")
            if self.on_exception_callback:
                self.on_exception_callback(self, e)
            if self.re_raise_exception:
                raise

    def create_task(self,
                    coroutine: Coroutine,
                    exception_callback: Callable[[Any, Exception], None],
                    custom_logger: Optional[logging.Logger] = None,
                    task_slug: str = '',
                    re_raise_exception: bool = True) -> asyncio.Task:
        """
        Create and return an asyncio task using the wrapped version of the provided coroutine.

        :param coroutine: The coroutine to be wrapped and run as a task.
        :param exception_callback: The callback to execute upon catching an exception.
        :param custom_logger: (Optional) A custom logger for logging exceptions. Defaults to None.
        :param task_slug: (Optional) A slug representing the task, useful for logging. Defaults to an empty string.
        :param re_raise_exception: (Optional) Whether to re-raise the caught exception. Defaults to True.
        :return: The created asyncio task running the wrapped coroutine.
        """
        self.on_exception_callback = exception_callback
        self.custom_logger = custom_logger
        self.re_raise_exception = re_raise_exception
        self.task_slug = task_slug
        self.task = asyncio.create_task(self.wrapped_coro(coroutine))
        return self.task
