from typing import List, Optional
from datetime import date
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.benefit import TariffBenefit, CustomsFeeRate, BRVRate
from app.schemas.benefit import TariffBenefitCreate, CustomsFeeRateCreate, BRVRateCreate


class CRUDTariffBenefit(CRUDBase[TariffBenefit, TariffBenefitCreate, TariffBenefitCreate]):
    async def get_by_tnved_code(
        self, 
        db: AsyncSession, 
        *, 
        tnved_code: str,
        check_date: Optional[date] = None
    ) -> List[TariffBenefit]:
        """TNVED kodga tegishli barcha imtiyozlarni olish"""
        if check_date is None:
            check_date = date.today()
        
        # Aniq kod bo'yicha yoki diapazon ichida qidirish
        query = select(TariffBenefit).filter(
            TariffBenefit.is_active == True,
            or_(
                # Aniq kod
                TariffBenefit.tnved_code == tnved_code,
                # Diapazon ichida
                and_(
                    TariffBenefit.tnved_code_start <= tnved_code,
                    or_(
                        TariffBenefit.tnved_code_end >= tnved_code,
                        TariffBenefit.tnved_code_end.is_(None)
                    )
                )
            ),
            # Amal qilish muddati
            or_(
                TariffBenefit.valid_from.is_(None),
                TariffBenefit.valid_from <= check_date
            ),
            or_(
                TariffBenefit.valid_until.is_(None),
                TariffBenefit.valid_until >= check_date
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_duty_exemption(
        self, 
        db: AsyncSession, 
        *, 
        tnved_code: str
    ) -> Optional[TariffBenefit]:
        """Poshina imtiyozini olish"""
        benefits = await self.get_by_tnved_code(db, tnved_code=tnved_code)
        for b in benefits:
            if b.benefit_type in ('duty_exempt', 'duty_reduction'):
                return b
        return None


class CRUDCustomsFeeRate(CRUDBase[CustomsFeeRate, CustomsFeeRateCreate, CustomsFeeRateCreate]):
    async def get_applicable_rate(
        self, 
        db: AsyncSession, 
        *, 
        customs_value: float
    ) -> Optional[CustomsFeeRate]:
        """Bojxona qiymatiga mos yig'im stavkasini olish"""
        query = select(CustomsFeeRate).filter(
            CustomsFeeRate.is_active == True,
            or_(
                CustomsFeeRate.min_customs_value.is_(None),
                CustomsFeeRate.min_customs_value <= customs_value
            ),
            or_(
                CustomsFeeRate.max_customs_value.is_(None),
                CustomsFeeRate.max_customs_value >= customs_value
            )
        )
        result = await db.execute(query)
        return result.scalars().first()


class CRUDBRVRate(CRUDBase[BRVRate, BRVRateCreate, BRVRateCreate]):
    async def get_current(self, db: AsyncSession) -> Optional[BRVRate]:
        """Joriy BRV qiymatini olish"""
        today = date.today()
        query = select(BRVRate).filter(
            BRVRate.is_active == True,
            BRVRate.valid_from <= today,
            or_(
                BRVRate.valid_until.is_(None),
                BRVRate.valid_until >= today
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_year(self, db: AsyncSession, *, year: int) -> Optional[BRVRate]:
        """Yil bo'yicha BRV olish"""
        result = await db.execute(
            select(BRVRate).filter(BRVRate.year == year)
        )
        return result.scalars().first()


tariff_benefit = CRUDTariffBenefit(TariffBenefit)
customs_fee_rate = CRUDCustomsFeeRate(CustomsFeeRate)
brv_rate = CRUDBRVRate(BRVRate)
