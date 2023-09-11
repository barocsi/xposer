import asyncio

async def longrunningscriptdelay(delay):
    await asyncio.sleep(delay)
    print(f"longrunok {delay}")

async def main_sequential():
    print("start 3")
    await longrunningscriptdelay(3)
    print("start 6")
    await longrunningscriptdelay(6)
    print("finish")

# Run the sequential version
asyncio.run(main_sequential())
