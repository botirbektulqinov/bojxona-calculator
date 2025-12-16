import asyncio
import sys
import os

sys.path.append(os.getcwd())

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.tnved import TNVedCode
from app.models.tariff import TariffRate
from app.models.currency import Currency
from datetime import date, datetime, timezone

async def seed():
    async with AsyncSessionLocal() as db:
        code = "8703231981"
        tnved = await db.get(TNVedCode, 1)
        if not tnved:
             tnved = TNVedCode(
                code=code,
                full_code=code,
                description="Vehicles with spark-ignition internal combustion piston engine...",
                level=4
            )
             db.add(tnved)
             await db.commit()
             await db.refresh(tnved)
             print(f"Added TNVED: {code}")
        tariff_obj = await db.scalar(select(TariffRate).where(TariffRate.tnved_id == tnved.id))
        if not tariff_obj:
            tariff = TariffRate(
                tnved_id=tnved.id,
                import_duty_percent=15.0,
                excise_percent=12.0,
                vat_percent=12.0,
                updated_at=datetime.now(timezone.utc)
            )
            db.add(tariff)
            await db.commit()
            print("Added Tariff Rates")
        curr = await db.get(Currency, 1)
        if not curr:
            c = Currency(
                code="USD",
                rate_uzs=12500.0,
                date=date.today(),
                is_active=True
            )
            db.add(c)
            await db.commit()
            print("Added Currency: USD")

if __name__ == "__main__":
    asyncio.run(seed())
