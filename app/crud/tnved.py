from typing import List, Optional
from sqlalchemy import select, case, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.tnved import TNVedCode
from app.schemas.tnved import TNVedCreate, TNVedUpdate

class CRUDTNVed(CRUDBase[TNVedCode, TNVedCreate, TNVedUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[TNVedCode]:
        # Perform exact match search
        result = await db.execute(select(TNVedCode).filter(TNVedCode.code == code))
        return result.scalars().first()

    async def search(self, db: AsyncSession, *, q: str, limit: int = 10) -> List[TNVedCode]:
        """
        TN VED kodlarini qidirish.
        
        Tartib:
        1. Kod boshidan mos keluvchilar (56 -> 5601, 5602...)
        2. Tavsifda so'z bor bo'lganlar
        
        Agar faqat raqamlar kiritilsa - kod bo'yicha qidirish ustunlik oladi.
        """
        q = q.strip()
        
        # Agar faqat raqamlar bo'lsa - kod bo'yicha qidirish
        if q.isdigit():
            # Avval aniq kod prefiksi bo'yicha
            query = select(TNVedCode).filter(
                TNVedCode.code.like(f"{q}%")
            ).order_by(
                # Qisqa kodlar birinchi (2 -> 4 -> 6 -> 8 -> 10 raqamli)
                func.length(TNVedCode.code),
                TNVedCode.code
            ).limit(limit)
        else:
            # Matn qidiruvida - kod yoki tavsif bo'yicha
            query = select(TNVedCode).filter(
                (TNVedCode.code.like(f"{q}%")) | 
                (TNVedCode.description.ilike(f"%{q}%"))
            ).order_by(
                # Kod bilan boshlanuvchilar birinchi
                case(
                    (TNVedCode.code.like(f"{q}%"), 0),
                    else_=1
                ),
                func.length(TNVedCode.code),
                TNVedCode.code
            ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def create_or_update(
        self, db: AsyncSession, *, obj_in: TNVedCreate
    ) -> TNVedCode:
        # Check if exists
        existing = await self.get_by_code(db, code=obj_in.code)
        if existing:
            return await self.update(db, db_obj=existing, obj_in=obj_in)
        return await self.create(db, obj_in=obj_in)

tnved = CRUDTNVed(TNVedCode)
