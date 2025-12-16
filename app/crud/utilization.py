from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.utilization import UtilizationFee
from app.schemas.utilization import UtilizationFeeCreate, UtilizationFeeUpdate


class CRUDUtilizationFee(CRUDBase[UtilizationFee, UtilizationFeeCreate, UtilizationFeeUpdate]):
    async def get_by_tnved_code(
        self, 
        db: AsyncSession, 
        *, 
        tnved_code: str,
        engine_volume: Optional[int] = None,
        vehicle_age: Optional[int] = None
    ) -> Optional[UtilizationFee]:
        """
        TNVED kodga mos utilizatsiya yig'imini olish.
        Avtomobillar uchun dvigatel hajmi va yoshi ham hisobga olinadi.
        """
        # Kod prefikslari bo'yicha qidirish (8703xxxx -> 8703 bilan solishtiriladi)
        # Eng uzun prefiksdan boshlab qidirish
        for prefix_len in range(len(tnved_code), 0, -1):
            prefix = tnved_code[:prefix_len]
            
            query = select(UtilizationFee).filter(
                UtilizationFee.is_active == True,
                or_(
                    # Aniq kod yoki prefiks
                    and_(
                        UtilizationFee.tnved_code_start == prefix,
                        UtilizationFee.tnved_code_end.is_(None)
                    ),
                    # Diapazon
                    and_(
                        UtilizationFee.tnved_code_start <= tnved_code,
                        UtilizationFee.tnved_code_end >= tnved_code
                    )
                )
            )
            
            result = await db.execute(query)
            fees = list(result.scalars().all())
            
            if not fees:
                continue
            
            # Agar avtomobil parametrlari berilgan bo'lsa, eng mosini tanlash
            if engine_volume is not None or vehicle_age is not None:
                for fee in fees:
                    # Dvigatel hajmi tekshiruvi
                    vol_match = True
                    if fee.engine_volume_min is not None or fee.engine_volume_max is not None:
                        if engine_volume is None:
                            continue
                        if fee.engine_volume_min and engine_volume < fee.engine_volume_min:
                            vol_match = False
                        if fee.engine_volume_max and engine_volume > fee.engine_volume_max:
                            vol_match = False
                    
                    # Yosh tekshiruvi
                    age_match = True
                    if fee.vehicle_age_min is not None or fee.vehicle_age_max is not None:
                        if vehicle_age is None:
                            continue
                        if fee.vehicle_age_min and vehicle_age < fee.vehicle_age_min:
                            age_match = False
                        if fee.vehicle_age_max and vehicle_age > fee.vehicle_age_max:
                            age_match = False
                    
                    if vol_match and age_match:
                        return fee
            else:
                # Birinchi mos keluvchini qaytarish
                return fees[0] if fees else None
        
        return None

    async def get_all_for_code_prefix(
        self, 
        db: AsyncSession, 
        *, 
        code_prefix: str
    ) -> List[UtilizationFee]:
        """Kod prefiksi bo'yicha barcha utilizatsiya yig'imlarini olish"""
        result = await db.execute(
            select(UtilizationFee).filter(
                UtilizationFee.is_active == True,
                UtilizationFee.tnved_code_start.startswith(code_prefix)
            )
        )
        return result.scalars().all()


utilization_fee = CRUDUtilizationFee(UtilizationFee)
