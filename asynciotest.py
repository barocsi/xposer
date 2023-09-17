import asyncio
import logging
from time import sleep

from xposer.api.base.xpose_task import XPTask


# Assuming the AIOTaskHelper class is defined above...

async def sample_coroutine(argfoo):
    print("Starting coroutine:", argfoo)
    await asyncio.sleep(2)
    raise ValueError("Sample error in coroutine!")  # Raise an error to test our exception handling

async def main():
    # Setup logging
    logging.basicConfig(level=logging.ERROR)

    # Create an AIOTaskHelper instance
    xp_task = XPTask().create_task(
        sample_coroutine('foo'),
        lambda context, exception: print(f"[Callback] Error in {context.task_type}: {exception}. Captured value: foobar"),
        None,
        'foobar')
    # Run the tasks for the sake of the example
    await asyncio.gather(xp_task, return_exceptions=True)
    sleep(1)


asyncio.run(main())
