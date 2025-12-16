import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.country import Country, FreeTradeCountry
from app.models.benefit import BRVRate, CustomsFeeRate
from app.models.utilization import UtilizationFee
from app.models.currency import Currency
from app.models.tnved import TNVedCode
from app.models.tariff import TariffRate

COUNTRIES = [
    {"code": "UZ", "name_uz": "O'zbekiston", "name_ru": "Узбекистан", "name_en": "Uzbekistan"},
    {"code": "RU", "name_uz": "Rossiya", "name_ru": "Россия", "name_en": "Russia"},
    {"code": "KZ", "name_uz": "Qozog'iston", "name_ru": "Казахстан", "name_en": "Kazakhstan"},
    {"code": "KG", "name_uz": "Qirg'iziston", "name_ru": "Кыргызстан", "name_en": "Kyrgyzstan"},
    {"code": "TJ", "name_uz": "Tojikiston", "name_ru": "Таджикистан", "name_en": "Tajikistan"},
    {"code": "TM", "name_uz": "Turkmaniston", "name_ru": "Туркменистан", "name_en": "Turkmenistan"},
    {"code": "BY", "name_uz": "Belarusiya", "name_ru": "Беларусь", "name_en": "Belarus"},
    {"code": "AM", "name_uz": "Armaniston", "name_ru": "Армения", "name_en": "Armenia"},
    {"code": "AZ", "name_uz": "Ozarbayjon", "name_ru": "Азербайджан", "name_en": "Azerbaijan"},
    {"code": "MD", "name_uz": "Moldova", "name_ru": "Молдова", "name_en": "Moldova"},
    {"code": "GE", "name_uz": "Gruziya", "name_ru": "Грузия", "name_en": "Georgia"},
    {"code": "UA", "name_uz": "Ukraina", "name_ru": "Украина", "name_en": "Ukraine"},
    {"code": "CN", "name_uz": "Xitoy", "name_ru": "Китай", "name_en": "China"},
    {"code": "TR", "name_uz": "Turkiya", "name_ru": "Турция", "name_en": "Turkey"},
    {"code": "KR", "name_uz": "Janubiy Koreya", "name_ru": "Южная Корея", "name_en": "South Korea"},
    {"code": "JP", "name_uz": "Yaponiya", "name_ru": "Япония", "name_en": "Japan"},
    {"code": "DE", "name_uz": "Germaniya", "name_ru": "Германия", "name_en": "Germany"},
    {"code": "US", "name_uz": "AQSH", "name_ru": "США", "name_en": "United States"},
    {"code": "GB", "name_uz": "Buyuk Britaniya", "name_ru": "Великобритания", "name_en": "United Kingdom"},
    {"code": "AE", "name_uz": "BAA", "name_ru": "ОАЭ", "name_en": "United Arab Emirates"},
    {"code": "IN", "name_uz": "Hindiston", "name_ru": "Индия", "name_en": "India"},
    {"code": "PK", "name_uz": "Pokiston", "name_ru": "Пакистан", "name_en": "Pakistan"},
    {"code": "AF", "name_uz": "Afg'oniston", "name_ru": "Афганистан", "name_en": "Afghanistan"},
    {"code": "IR", "name_uz": "Eron", "name_ru": "Иран", "name_en": "Iran"},
    {"code": "SA", "name_uz": "Saudiya Arabistoni", "name_ru": "Саудовская Аравия", "name_en": "Saudi Arabia"},
    {"code": "IT", "name_uz": "Italiya", "name_ru": "Италия", "name_en": "Italy"},
    {"code": "FR", "name_uz": "Fransiya", "name_ru": "Франция", "name_en": "France"},
    {"code": "PL", "name_uz": "Polsha", "name_ru": "Польша", "name_en": "Poland"},
    {"code": "NL", "name_uz": "Niderlandiya", "name_ru": "Нидерланды", "name_en": "Netherlands"},
    {"code": "CZ", "name_uz": "Chexiya", "name_ru": "Чехия", "name_en": "Czech Republic"},
    {"code": "XX", "name_uz": "Noma'lum", "name_ru": "Неизвестно", "name_en": "Unknown"},
]
FREE_TRADE_COUNTRIES = [
    {"country_code": "RU", "country_name": "Rossiya Federatsiyasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "KZ", "country_name": "Qozog'iston Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "KG", "country_name": "Qirg'iziston Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "TJ", "country_name": "Tojikiston Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "BY", "country_name": "Belarusiya Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "AM", "country_name": "Armaniston Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "MD", "country_name": "Moldova Respublikasi", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "UA", "country_name": "Ukraina", "agreement_name": "MDH Erkin savdo shartnomasi", "requires_certificate": True},
    {"country_code": "AZ", "country_name": "Ozarbayjon Respublikasi", "agreement_name": "Ikki tomonlama shartnoma", "requires_certificate": True},
    {"country_code": "GE", "country_name": "Gruziya", "agreement_name": "Ikki tomonlama shartnoma", "requires_certificate": True},
]

BRV_RATES = [
    {"year": 2023, "amount": 330000, "valid_from": date(2023, 1, 1), "valid_until": date(2023, 12, 31)},
    {"year": 2024, "amount": 340000, "valid_from": date(2024, 1, 1), "valid_until": date(2024, 12, 31)},
    {"year": 2025, "amount": 375000, "valid_from": date(2025, 1, 1), "valid_until": None},  
]
CUSTOMS_FEE_RATES = [
    {
        "min_customs_value": 0,
        "max_customs_value": None,
        "fee_type": "percent",
        "fee_value": 0.2,  
        "min_fee": 50000,  
        "max_fee": 3000000,  
        "description": "Standart bojxona rasmiylash yig'imi"
    }
]

UTILIZATION_FEES = [
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 6.5,
        "engine_volume_max": 1000,
        "description": "Yengil avtomobil, dvigatel hajmi 1000 sm³ gacha"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 9.2,
        "engine_volume_min": 1001,
        "engine_volume_max": 1500,
        "description": "Yengil avtomobil, dvigatel hajmi 1001-1500 sm³"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 13.8,
        "engine_volume_min": 1501,
        "engine_volume_max": 1800,
        "description": "Yengil avtomobil, dvigatel hajmi 1501-1800 sm³"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 17.3,
        "engine_volume_min": 1801,
        "engine_volume_max": 2000,
        "description": "Yengil avtomobil, dvigatel hajmi 1801-2000 sm³"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 23.0,
        "engine_volume_min": 2001,
        "engine_volume_max": 2300,
        "description": "Yengil avtomobil, dvigatel hajmi 2001-2300 sm³"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 27.6,
        "engine_volume_min": 2301,
        "engine_volume_max": 3000,
        "description": "Yengil avtomobil, dvigatel hajmi 2301-3000 sm³"
    },
    {
        "tnved_code_start": "8703",
        "fee_type": "brv_multiplier",
        "brv_multiplier": 46.0,
        "engine_volume_min": 3001,
        "description": "Yengil avtomobil, dvigatel hajmi 3000 sm³ dan yuqori"
    },
]


async def seed_countries(db: AsyncSession):
    print("Seeding countries...")
    for c in COUNTRIES:
        existing = await db.execute(
            Country.__table__.select().where(Country.code == c["code"])
        )
        if not existing.first():
            db.add(Country(**c, is_active=True))
    await db.commit()
    print(f"Added {len(COUNTRIES)} countries")


async def seed_free_trade_countries(db: AsyncSession):
    print("Seeding free trade countries...")
    for ftc in FREE_TRADE_COUNTRIES:
        existing = await db.execute(
            FreeTradeCountry.__table__.select().where(FreeTradeCountry.country_code == ftc["country_code"])
        )
        if not existing.first():
            db.add(FreeTradeCountry(**ftc, is_active=True))
    await db.commit()
    print(f"Added {len(FREE_TRADE_COUNTRIES)} free trade countries")


async def seed_brv_rates(db: AsyncSession):
    print("Seeding BRV rates...")
    for brv in BRV_RATES:
        existing = await db.execute(
            BRVRate.__table__.select().where(BRVRate.year == brv["year"])
        )
        if not existing.first():
            db.add(BRVRate(**brv, is_active=True))
    await db.commit()
    print(f"Added {len(BRV_RATES)} BRV rates")


async def seed_customs_fee_rates(db: AsyncSession):
    print("Seeding customs fee rates...")
    for cfr in CUSTOMS_FEE_RATES:
        db.add(CustomsFeeRate(**cfr, is_active=True))
    await db.commit()
    print(f"Added {len(CUSTOMS_FEE_RATES)} customs fee rates")


async def seed_utilization_fees(db: AsyncSession):
    print("Seeding utilization fees...")
    for uf in UTILIZATION_FEES:
        db.add(UtilizationFee(**uf, is_active=True, source_url="https://lex.uz/docs/4848953"))
    await db.commit()
    print(f"Added {len(UTILIZATION_FEES)} utilization fees")


async def seed_currencies(db: AsyncSession):
    print("Seeding currencies...")
    from datetime import date as dt
    today = dt.today()
    default_currencies = [
        {"code": "USD", "rate_uzs": 12850.0, "date": today},
        {"code": "EUR", "rate_uzs": 14100.0, "date": today},
        {"code": "RUB", "rate_uzs": 130.0, "date": today},
        {"code": "KZT", "rate_uzs": 26.0, "date": today},
        {"code": "CNY", "rate_uzs": 1770.0, "date": today},
    ]
    for curr in default_currencies:
        existing = await db.execute(
            Currency.__table__.select().where(Currency.code == curr["code"])
        )
        if not existing.first():
            db.add(Currency(**curr))
    await db.commit()
    print(f"Added {len(default_currencies)} currencies")


async def main():
    print("Starting database seeding...")    
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        await seed_currencies(db)
        await seed_countries(db)
        await seed_free_trade_countries(db)
        await seed_brv_rates(db)
        await seed_customs_fee_rates(db)
        await seed_utilization_fees(db)
    
    await engine.dispose()
    print("Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())
