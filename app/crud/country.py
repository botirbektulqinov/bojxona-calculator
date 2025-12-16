from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.country import Country, FreeTradeCountry
from app.schemas.country import CountryCreate, CountryUpdate, FreeTradeCountryCreate


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Country]:
        result = await db.execute(
            select(Country).filter(Country.code == code.upper())
        )
        return result.scalars().first()

    async def get_all_active(self, db: AsyncSession) -> List[Country]:
        result = await db.execute(
            select(Country).filter(Country.is_active == True).order_by(Country.name_uz)
        )
        return result.scalars().all()

    async def search(self, db: AsyncSession, *, q: str, limit: int = 20) -> List[Country]:
        result = await db.execute(
            select(Country).filter(
                (Country.code.ilike(f"{q}%")) |
                (Country.name_uz.ilike(f"%{q}%")) |
                (Country.name_en.ilike(f"%{q}%"))
            ).filter(Country.is_active == True).limit(limit)
        )
        return result.scalars().all()


class CRUDFreeTradeCountry(CRUDBase[FreeTradeCountry, FreeTradeCountryCreate, FreeTradeCountryCreate]):
    async def get_by_code(self, db: AsyncSession, *, country_code: str) -> Optional[FreeTradeCountry]:
        result = await db.execute(
            select(FreeTradeCountry).filter(
                FreeTradeCountry.country_code == country_code.upper(),
                FreeTradeCountry.is_active == True
            )
        )
        return result.scalars().first()

    async def is_free_trade(self, db: AsyncSession, *, country_code: str) -> bool:
        """Tekshirish: mamlakat erkin savdo zonasidami?"""
        result = await self.get_by_code(db, country_code=country_code)
        return result is not None

    async def get_all(self, db: AsyncSession) -> List[FreeTradeCountry]:
        result = await db.execute(
            select(FreeTradeCountry).filter(FreeTradeCountry.is_active == True)
        )
        return result.scalars().all()


country = CRUDCountry(Country)
free_trade_country = CRUDFreeTradeCountry(FreeTradeCountry)
