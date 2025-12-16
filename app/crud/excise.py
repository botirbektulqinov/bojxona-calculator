"""Aksiz stavkalari CRUD operatsiyalari"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.excise import ExciseRate


class CRUDExcise:
    """Aksiz stavkalari uchun CRUD"""
    
    async def get_by_tnved_code(
        self, 
        db: AsyncSession, 
        tnved_code: str
    ) -> Optional[ExciseRate]:
        """TN VED kodi bo'yicha aksiz stavkasini topish"""
        
        # Barcha faol aksiz stavkalarini olish
        result = await db.execute(
            select(ExciseRate).where(ExciseRate.is_active == True)
        )
        all_excise = result.scalars().all()
        
        # Eng mos keluvchisini topish (prefix bo'yicha)
        best_match: Optional[ExciseRate] = None
        best_match_len = 0
        
        for excise in all_excise:
            if not excise.tnved_codes:
                continue
            
            # tnved_codes maydonida vergul bilan ajratilgan kodlar bo'lishi mumkin
            codes = [c.strip() for c in excise.tnved_codes.split(",")]
            
            for code in codes:
                # Agar berilgan TN VED kodi shu code bilan boshlansa
                if tnved_code.startswith(code):
                    if len(code) > best_match_len:
                        best_match = excise
                        best_match_len = len(code)
                # Yoki agar aksiz kodi berilgan TN VED kodi bilan boshlansa (qisqa kodlar uchun)
                elif code.startswith(tnved_code[:len(code)]):
                    if len(code) > best_match_len:
                        best_match = excise
                        best_match_len = len(code)
        
        return best_match
    
    async def get_by_category(
        self, 
        db: AsyncSession, 
        category: str
    ) -> List[ExciseRate]:
        """Kategoriya bo'yicha barcha aksiz stavkalarini olish"""
        result = await db.execute(
            select(ExciseRate).where(
                ExciseRate.category == category,
                ExciseRate.is_active == True
            )
        )
        return list(result.scalars().all())
    
    async def get_all(self, db: AsyncSession) -> List[ExciseRate]:
        """Barcha faol aksiz stavkalarini olish"""
        result = await db.execute(
            select(ExciseRate).where(ExciseRate.is_active == True)
        )
        return list(result.scalars().all())


excise = CRUDExcise()
