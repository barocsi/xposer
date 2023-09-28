import asyncio
from datetime import time
from functools import partial
from time import sleep


def blocking_io(slug,sleeptime):
    print(f"start blocking_io {slug}\n")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    sleep(sleeptime)
    raise Exception(f"KOCSOGOLES from {slug}")
    print(f"blocking_io complete {slug}\n")

async def main():
    print(f"started main")
    bl1 = partial(blocking_io,'fasz',3)
    bl2 = partial(blocking_io,'geci',2)
    future1 = asyncio.run_coroutine_threadsafe(bl1, asyncio.new_event_loop())
    future2 = asyncio.run_coroutine_threadsafe(bl2, asyncio.new_event_loop())

    print(f"finished main")


asyncio.run(main())