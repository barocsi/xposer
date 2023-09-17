import asyncio
import logging


class XPTask:
    def __init__(self):
        self.task = None
        self.task_slug = None
        self.custom_logger = None
        self.on_exception_callback = None

    @property
    def logger(self) -> logging.Logger:
        return self.custom_logger or logging.getLogger(self.task_slug)

    async def wrapped_coro(self, coroutine):
        try:
            await coroutine
        except Exception as e:
            self.logger.error(f"Caught exception in {self.task_slug}: {e}")
            if self.on_exception_callback:
                self.on_exception_callback(self, e)

    def create_task(self, coroutine, exception_callback, custom_logger, task_slug):
        self.on_exception_callback = exception_callback
        self.custom_logger = custom_logger
        self.task_slug = task_slug
        self.task = asyncio.create_task(self.wrapped_coro(coroutine))
        return self.task
