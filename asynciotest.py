import asyncio

def getnamefromuri():
    # ... your sync function: httploaduri ...
    return result

async def wrap_in_asyncio(callback):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, getnamefromuri)
    callback(result)

def my_callback(result):
    print(f"Received result: {result}")

# To use
async def main():
    await wrap_in_asyncio(my_callback)

asyncio.run(main())