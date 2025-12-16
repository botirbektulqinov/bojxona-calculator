import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.parsers.currency_updater import CurrencyUpdater

async def main():
    print("Updating currency rates...")
    updater = CurrencyUpdater()
    
    async with AsyncSessionLocal() as db:
        await updater.update_rates(db)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
