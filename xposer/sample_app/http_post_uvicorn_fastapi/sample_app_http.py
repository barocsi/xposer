# In your main module
import asyncio

from xposer.core.boot import Boot


async def main():
    try:
        await Boot().boot()
    except SystemExit:
        pass  # Handle graceful shutdown here if needed


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass  # Handle graceful shutdown here if needed
