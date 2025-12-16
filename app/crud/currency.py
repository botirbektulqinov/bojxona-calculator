from datetime import date
from typing import List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate

class CRUDCurrency(CRUDBase[Currency, CurrencyCreate, CurrencyUpdate]):
    async def get_by_code_and_date(self, db: AsyncSession, *, code: str, date_obj: date) -> Optional[Currency]:
        result = await db.execute(
            select(Currency).filter(Currency.code == code, Currency.date == date_obj)
        )
        return result.scalars().first()

    async def get_latest_rate(self, db: AsyncSession, code: str = "USD") -> Optional[Currency]:
        """Eng oxirgi kursni olish."""
        result = await db.execute(
            select(Currency)
            .where(Currency.code == code, Currency.is_active == True)
            .order_by(desc(Currency.date))
            .limit(1)
        )
        return result.scalars().first()

    async def get_latest_rates(self, db: AsyncSession) -> List[Currency]:
        """Har bir valyuta uchun eng oxirgi kurslar."""
        # Subquery: har bir valyuta uchun eng oxirgi sana
        subq = (
            select(Currency.code, func.max(Currency.date).label("max_date"))
            .where(Currency.is_active == True)
            .group_by(Currency.code)
            .subquery()
        )
        
        result = await db.execute(
            select(Currency)
            .join(subq, (Currency.code == subq.c.code) & (Currency.date == subq.c.max_date))
            .where(Currency.is_active == True)
            .order_by(Currency.code)
        )
        return result.scalars().all()
    
    async def get_all_active(self, db: AsyncSession) -> List[Currency]:
        """Barcha aktiv valyutalar (faqat eng oxirgi)."""
        return await self.get_latest_rates(db)
    
    async def upsert(self, db: AsyncSession, *, obj_in: CurrencyCreate) -> Currency:
        existing = await self.get_by_code_and_date(db, code=obj_in.code, date_obj=obj_in.date)
        if existing:
            return await self.update(db, db_obj=existing, obj_in=obj_in)
        return await self.create(db, obj_in=obj_in)


currency = CRUDCurrency(Currency)
