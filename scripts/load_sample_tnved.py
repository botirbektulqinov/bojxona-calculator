#!/usr/bin/env python
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.tnved import TNVedCode
from app.models.tariff import TariffRate
SAMPLE_TNVED = [
    # Avtomobillar
    {"code": "8703", "description": "Avtomobillar va boshqa avtotransport vositalari (yengil avtomobillar)", "level": 4},
    {"code": "870321", "description": "Dvigatel hajmi 1000 sm³ dan oshmaydigan avtomobillar", "level": 6},
    {"code": "870322", "description": "Dvigatel hajmi 1000 sm³ dan 1500 sm³ gacha bo'lgan avtomobillar", "level": 6},
    {"code": "870323", "description": "Dvigatel hajmi 1500 sm³ dan 3000 sm³ gacha bo'lgan avtomobillar", "level": 6},
    {"code": "870324", "description": "Dvigatel hajmi 3000 sm³ dan ortiq bo'lgan avtomobillar", "level": 6},
    {"code": "8703231981", "description": "Yangi yengil avtomobillar, 1500-2000 sm³", "level": 10},
    {"code": "8703231982", "description": "Ishlatilgan yengil avtomobillar, 1500-2000 sm³", "level": 10},
    
    # Elektronika
    {"code": "8471", "description": "Avtomatik ma'lumotlarni qayta ishlash mashinalari (kompyuterlar)", "level": 4},
    {"code": "847130", "description": "Portativ raqamli kompyuterlar (noutbuklar)", "level": 6},
    {"code": "8471300000", "description": "Noutbuklar va portativ kompyuterlar", "level": 10},
    
    {"code": "8517", "description": "Telefon apparatlari, mobil telefonlar", "level": 4},
    {"code": "851712", "description": "Mobil telefonlar", "level": 6},
    {"code": "8517120000", "description": "Mobil telefonlar (smartfonlar)", "level": 10},
    
    {"code": "8528", "description": "Televizorlar, monitorlar", "level": 4},
    {"code": "852872", "description": "Boshqa televizorlar, rangli", "level": 6},
    {"code": "8528720000", "description": "Rangli televizorlar", "level": 10},
    
    # Kiyim-kechak
    {"code": "6201", "description": "Erkaklar va o'g'il bolalar uchun palto, kurtka", "level": 4},
    {"code": "620111", "description": "Jundan yoki nozik yunli hayvon junidan palto", "level": 6},
    {"code": "6201110000", "description": "Erkaklar uchun jun palto", "level": 10},
    
    {"code": "6203", "description": "Erkaklar kostyumlari, shimlar", "level": 4},
    {"code": "620342", "description": "Paxtadan shimlar", "level": 6},
    {"code": "6203420000", "description": "Erkaklar uchun paxta shimlar (jinslar)", "level": 10},
    
    # Oziq-ovqat
    {"code": "0201", "description": "Mol go'shti, yangi yoki muzlatilgan", "level": 4},
    {"code": "020110", "description": "Mol go'shti, yangi", "level": 6},
    {"code": "0201100000", "description": "Mol go'shti, yangi, suyakli", "level": 10},
    
    {"code": "0402", "description": "Sut va qaymog'", "level": 4},
    {"code": "040221", "description": "Quruq sut", "level": 6},
    {"code": "0402210000", "description": "Quruq sut, yog'siz", "level": 10},
    
    # Mashinalar
    {"code": "8429", "description": "Buldozerlar, ekskavatorlar", "level": 4},
    {"code": "842951", "description": "Frontal yuklash asboblari", "level": 6},
    {"code": "8429510000", "description": "Frontal yuklagichlar", "level": 10},
    
    # Mebellar
    {"code": "9401", "description": "O'rindiqlar va stullar", "level": 4},
    {"code": "940161", "description": "Yog'ochdan qoplamali o'rindiqlar", "level": 6},
    {"code": "9401610000", "description": "Yog'och o'rindiqlar, qoplamali", "level": 10},
    
    {"code": "9403", "description": "Boshqa mebellar", "level": 4},
    {"code": "940330", "description": "Ofis mebellari", "level": 6},
    {"code": "9403300000", "description": "Yog'och ofis mebellari", "level": 10},
]
SAMPLE_TARIFFS = [
    # Avtomobillar - yuqori boj
    {"tnved_code": "8703", "duty_rate": 30.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "870321", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "870322", "duty_rate": 25.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "870323", "duty_rate": 30.0, "excise_rate": 5.0, "vat_rate": 12.0},
    {"tnved_code": "870324", "duty_rate": 50.0, "excise_rate": 10.0, "vat_rate": 12.0},
    {"tnved_code": "8703231981", "duty_rate": 30.0, "excise_rate": 5.0, "vat_rate": 12.0},
    {"tnved_code": "8703231982", "duty_rate": 50.0, "excise_rate": 10.0, "vat_rate": 12.0},
    
    # Elektronika - o'rtacha boj
    {"tnved_code": "8471", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "847130", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "8471300000", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    
    {"tnved_code": "8517", "duty_rate": 5.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "851712", "duty_rate": 5.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "8517120000", "duty_rate": 5.0, "excise_rate": None, "vat_rate": 12.0},
    
    {"tnved_code": "8528", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "852872", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "8528720000", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    
    # Kiyim - o'rtacha boj
    {"tnved_code": "6201", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "620111", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "6201110000", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    
    {"tnved_code": "6203", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "620342", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "6203420000", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    
    # Oziq-ovqat - past boj
    {"tnved_code": "0201", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "020110", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "0201100000", "duty_rate": 15.0, "excise_rate": None, "vat_rate": 12.0},
    
    {"tnved_code": "0402", "duty_rate": 10.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "040221", "duty_rate": 10.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "0402210000", "duty_rate": 10.0, "excise_rate": None, "vat_rate": 12.0},
    
    # Mashinalar
    {"tnved_code": "8429", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "842951", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "8429510000", "duty_rate": 0.0, "excise_rate": None, "vat_rate": 12.0},
    
    # Mebellar
    {"tnved_code": "9401", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "940161", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "9401610000", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    
    {"tnved_code": "9403", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "940330", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
    {"tnved_code": "9403300000", "duty_rate": 20.0, "excise_rate": None, "vat_rate": 12.0},
]


async def main():
    print("🔢 TNVED kodlar va tariflarni yuklamoqda...")
    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        for item in SAMPLE_TNVED:
            existing = await session.execute(
                TNVedCode.__table__.select().where(TNVedCode.code == item["code"])
            )
            if not existing.first():
                session.add(TNVedCode(**item, is_active=True))
        
        await session.commit()
        print(f"✅ {len(SAMPLE_TNVED)} ta TNVED kod yuklandi")
        
        for item in SAMPLE_TARIFFS:
            existing = await session.execute(
                TariffRate.__table__.select().where(TariffRate.tnved_code == item["tnved_code"])
            )
            if not existing.first():
                session.add(TariffRate(**item, is_active=True))
        
        await session.commit()
        print(f"✅ {len(SAMPLE_TARIFFS)} ta tarif yuklandi")
    
    await engine.dispose()
    print("✅ Tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
