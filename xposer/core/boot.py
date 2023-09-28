import asyncio
import queue
import signal
from functools import partial

from xposer.api.base.xpose_task import XPTask
from xposer.core.configuration_model import ConfigModel
from xposer.core.configure import Configurator
from xposer.core.context import Context
from xposer.core.facade_factory import FacadeFactory
from xposer.core.logger import get_logger

"""
Boot sequence
1. Loads config and other contextual parameters
2. Instantiates facade
3. Creates an XPTask that manages the threadifying of the facade start services. A Facade can start multiple stuff inside of it that we dont know about therefore all of it is in a thread in async mode
4. XPTask exceptions propagate using threadsafe queue mechanisms, once XPTask receives error running on its internal loop exception handler it will send it to the queue defined upon xptastks __init__ instantiation stage
5. At the end all parallel tasks, monitoring and shutdown requests are processed
"""
class Boot:
    def __init__(self):
        self.ctx: Context = None
        self.shutdown_event = asyncio.Event()  # Shutdown event

    async def shutdown(self):
        self.ctx.logger.info(f"Shutting down application")
        await self.ctx.facade.tearDownApp()
        await asyncio.sleep(1)
        self.ctx.logger.info(f"Shutting down completed")
        self.shutdown_event.set()  # Set the shutdown event

    def _sync_shutdown_handler(self, a, b):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.shutdown())

    async def monitor_exceptions(self):
        while True:
            try:
                exception = self.ctx.exception_queue.get_nowait()
                self.ctx.logger.error(f"Raising exception from boot monitor_exceptions {exception}")
                raise exception
            except queue.Empty:
                await asyncio.sleep(1)  # a

    def handle_loop_exceptions(self, loop, context):
        task = context.get('future')
        if task:
            exception = task.exception()
            if exception:
                print(f"Main Boot thread caught loop exception: {exception}")
                loop.stop()
                raise exception

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

        # Forever running tasks in separate thread
        XPTask(self.ctx).create_task(
            to_be_coroutinified_partial_func=partial(facade.startFacadeServices, 'foo'),
            exception_callback=None,
            custom_logger=logger,
            task_slug='boot_facade_startFacadeServices',
            re_raise_exception=True)

        context.facade = facade

        # Add graceful shutdown feature
        # Signal handling setup
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, self._sync_shutdown_handler)

        # Exceptions (global handling)
        asyncio.get_event_loop().set_exception_handler(self.handle_loop_exceptions)

        # Verbose
        logger.info(f"Boot sequence completed successfully. Facade {facade.name} started")
        logger.debug(f"List of loaded configurations:")
        logger.debug(f"Facade level:")
        logger.debug(context.facade.config.model_dump_json(indent=4))
        logger.debug(f"Application level:")
        logger.debug(context.facade.app.config.model_dump_json(indent=4))

        try:
            await asyncio.gather(self.monitor_exceptions(), self.shutdown_event.wait(), return_exceptions=False)
        except Exception as e:
            self.ctx.logger.error(f"Caught exception: {e}")
            await self.shutdown()  # Call your shutdown function
            raise e  # Propagate the exception or handle it as needed

        return context
