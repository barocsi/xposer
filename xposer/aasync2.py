import asyncio

async def longrunningscriptdelay(delay):
    await asyncio.sleep(delay)
    print("longrunok")

async def main_concurrent():
    print("start")
    # Schedule the coroutine to run and move on immediately
    asyncio.create_task(longrunningscriptdelay(5))
    print("finish")

# Run the concurrent version
asyncio.run(main_concurrent())
