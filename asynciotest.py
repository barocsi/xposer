import os
import time
from threading import Thread
import queue
from pprint import pprint
import asyncio

exception_queue = queue.Queue()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def exception_handler(loop, context):
    print('Exception handler called')
    pprint(context)

def future_callback(fut):
    try:
        print("Success:", fut.result())
    except Exception as e:
        print("Exception:", e)
        exception_queue.put(e)

async def startProcess(name):
    time.sleep(3)
    try:
        dfdf  # This is undefined and will raise an error
        print(' Started-----------> ', name)

        while True:
            print("Sleeping...", name)
            time.sleep(5)

        return "Thread finish"

    except Exception as e:
        raise e

async def main_app():
    loop1 = asyncio.new_event_loop()
    loop1.set_exception_handler(exception_handler)

    process1_Thread = Thread(target=start_loop, args=(loop1,))
    process1_Thread.start()
    print("LOFASZ")

    fut = asyncio.run_coroutine_threadsafe(startProcess("Thread1"), loop1)
    fut.add_done_callback(future_callback)

    print("GECI")

    # Consume signaling
    while True:
        print("Sleeping main thread...")
        time.sleep(1)

        # Check for exceptions in the queue
        try:
            exception = exception_queue.get_nowait()
            print(f"Caught an exception from a child thread: {exception}")
        except queue.Empty:
            pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_app())
    finally:
        print("Exit...")
