from typing import Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.tariff import TariffRate
from app.models.tnved import TNVedCode
from app.schemas.tariff import TariffRateCreate, TariffRateUpdate

class CRUDTariff(CRUDBase[TariffRate, TariffRateCreate, TariffRateUpdate]):
    async def get_by_tnved_id(self, db: AsyncSession, *, tnved_id: int) -> Optional[TariffRate]:
        result = await db.execute(select(TariffRate).filter(TariffRate.tnved_id == tnved_id))
        return result.scalars().first()
    
    async def get_by_code_prefix(self, db: AsyncSession, *, code: str) -> Optional[TariffRate]:
        """
        Kod bo'yicha tarif topish - iyerarxik qidiruv.
        
        Qidiruv tartibi:
        1. Kod bilan boshlanadigan uzunroq kodlardan (bola-kodlar)
        2. Agar topilmasa, kodning prefixlari bo'yicha (ota-kodlar)
        
        Masalan: 87032310 -> avval 8703231xxx dan, keyin 8703231, 870323, 87032 dan qidiradi
        """
        # 1. Avval bola-kodlardan qidirish (uzunroq kodlar)
        # substr ishlatamiz - kod boshlanishi mos kelishi kerak
        query = text("""
            SELECT tr.* FROM tariff_rates tr
            JOIN tn_ved_codes t ON tr.tnved_id = t.id
            WHERE substr(t.code, 1, :code_len) = :code
            AND length(t.code) > :code_len
            AND tr.import_duty_percent IS NOT NULL
            ORDER BY t.code
            LIMIT 1
        """)
        
        result = await db.execute(query, {"code": code, "code_len": len(code)})
        row = result.fetchone()
        
        if row:
            return self._row_to_tariff(row)
        
        # 2. Agar bola-kodlarda topilmasa, ota-kodlardan qidirish
        # Kodning qisqartirilgan versiyalari bo'yicha
        for prefix_len in range(len(code) - 1, 3, -1):
            prefix = code[:prefix_len]
            query2 = text("""
                SELECT tr.* FROM tariff_rates tr
                JOIN tn_ved_codes t ON tr.tnved_id = t.id
                WHERE t.code = :prefix
                AND tr.import_duty_percent IS NOT NULL
                LIMIT 1
            """)
            result2 = await db.execute(query2, {"prefix": prefix})
            row2 = result2.fetchone()
            if row2:
                return self._row_to_tariff(row2)
        
        return None
    
    def _row_to_tariff(self, row) -> TariffRate:
        """SQL row dan TariffRate obyekt yaratish"""
        return TariffRate(
            id=row.id,
            tnved_id=row.tnved_id,
            import_duty_percent=row.import_duty_percent,
            import_duty_specific=row.import_duty_specific,
            specific_unit=row.specific_unit,
            excise_percent=row.excise_percent,
            excise_specific=row.excise_specific,
            vat_percent=row.vat_percent,
            source_url=row.source_url
        )

tariff = CRUDTariff(TariffRate)
