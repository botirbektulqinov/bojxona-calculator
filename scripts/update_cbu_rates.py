#!/usr/bin/env python
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.parsers.currency_updater import CurrencyUpdater
from app.db.base import Base
from app.models.currency import Currency


async def main():
    print(" CBU valyuta kurslarini yuklamoqda...")
    print(f"   API: https://cbu.uz/uz/arkhiv-kursov-valyut/json/")
    print()
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        updater = CurrencyUpdater(load_all=True)
        result = await updater.update_rates(session)
        
        print(f" {result['updated']} ta valyuta yangilandi")
        
        if result.get("errors"):
            print(f" Xatolar:")
            for err in result["errors"]:
                print(f"   - {err}")
        
        if result.get("rates"):
            print()
            print(" Asosiy kurslar:")
            for code in ["USD", "EUR", "RUB", "CNY", "GBP"]:
                if code in result["rates"]:
                    print(f"   {code}: {result['rates'][code]:,.2f} so'm")
    
    await engine.dispose()
    print()
    print("Tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
