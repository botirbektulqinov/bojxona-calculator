"""
O'zbekiston Markaziy Banki (CBU) valyuta kurslarini yangilash moduli.

API: https://cbu.uz/uz/arkhiv-kursov-valyut/json/

Javob formati:
{
    "id": 69,
    "Code": "840",
    "Ccy": "USD",
    "CcyNm_RU": "Доллар США",
    "CcyNm_UZ": "AQSH dollari",
    "CcyNm_UZC": "АҚШ доллари",
    "CcyNm_EN": "US Dollar",
    "Nominal": "1",
    "Rate": "12047.45",
    "Diff": "26.55",
    "Date": "12.12.2025"
}
"""
import httpx
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.currency import Currency as CurrencyModel
from app.schemas.currency import CurrencyCreate

# CBU API URL - rasmiy Markaziy Bank API
CBU_API_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"

# Asosiy valyutalar (import qilishda ko'p ishlatiladigan)
PRIMARY_CURRENCIES = ["USD", "EUR", "RUB", "CNY", "JPY", "GBP", "KRW", "TRY"]


class CurrencyUpdater:
    """CBU API orqali valyuta kurslarini yangilash."""
    
    def __init__(self, load_all: bool = True):
        """
        Args:
            load_all: True - barcha valyutalarni yuklash, 
                      False - faqat PRIMARY_CURRENCIES
        """
        self.load_all = load_all
    
    async def fetch_rates(self) -> List[dict]:
        """CBU API dan kurslarni olish."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CBU_API_URL)
            response.raise_for_status()
            return response.json()
    
    async def update_rates(self, db: AsyncSession) -> dict:
        """
        CBU dan valyuta kurslarini olish va bazaga saqlash.
        
        Returns:
            dict: {updated: int, errors: list}
        """
        result = {"updated": 0, "errors": [], "rates": {}}
        
        try:
            data = await self.fetch_rates()
            
            for item in data:
                code = item.get("Ccy", "")
                
                # Agar faqat asosiy valyutalar kerak bo'lsa
                if not self.load_all and code not in PRIMARY_CURRENCIES:
                    continue
                
                try:
                    # Parse rate
                    rate_str = item.get("Rate", "0")
                    rate = float(rate_str.replace(",", "."))
                    
                    # Parse nominal
                    nominal_str = item.get("Nominal", "1")
                    nominal = int(nominal_str) if nominal_str else 1
                    
                    # Parse diff
                    diff_str = item.get("Diff", "0")
                    diff = float(diff_str.replace(",", ".")) if diff_str else 0.0
                    
                    # Parse date (format: dd.mm.yyyy)
                    date_str = item.get("Date", "")
                    dt = datetime.strptime(date_str, "%d.%m.%Y").date()
                    
                    # CBU ID
                    cbu_id = item.get("id")
                    
                    # Upsert currency
                    await self._upsert_currency(
                        db=db,
                        code=code,
                        name=item.get("CcyNm_UZ", ""),
                        name_ru=item.get("CcyNm_RU", ""),
                        name_en=item.get("CcyNm_EN", ""),
                        nominal=nominal,
                        rate_uzs=rate,
                        diff=diff,
                        date=dt,
                        cbu_id=cbu_id
                    )
                    
                    result["updated"] += 1
                    result["rates"][code] = rate
                    
                except Exception as e:
                    result["errors"].append(f"{code}: {str(e)}")
            
            await db.commit()
            
        except httpx.HTTPError as e:
            result["errors"].append(f"HTTP xatosi: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Umumiy xato: {str(e)}")
        
        return result
    
    async def _upsert_currency(
        self,
        db: AsyncSession,
        code: str,
        name: str,
        name_ru: str,
        name_en: str,
        nominal: int,
        rate_uzs: float,
        diff: float,
        date: date,
        cbu_id: Optional[int] = None
    ):
        """Valyutani yangilash yoki yaratish."""
        # Mavjud yozuvni topish
        stmt = select(CurrencyModel).where(
            CurrencyModel.code == code,
            CurrencyModel.date == date
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Yangilash
            existing.name = name
            existing.name_ru = name_ru
            existing.name_en = name_en
            existing.nominal = nominal
            existing.rate_uzs = rate_uzs
            existing.diff = diff
            existing.cbu_id = cbu_id
            existing.is_active = True
        else:
            # Yangi yaratish
            new_currency = CurrencyModel(
                code=code,
                name=name,
                name_ru=name_ru,
                name_en=name_en,
                nominal=nominal,
                rate_uzs=rate_uzs,
                diff=diff,
                date=date,
                cbu_id=cbu_id,
                is_active=True
            )
            db.add(new_currency)
    
    async def get_rate(self, db: AsyncSession, code: str = "USD") -> Optional[float]:
        """
        Valyuta kursini olish.
        
        Args:
            code: Valyuta kodi (USD, EUR, RUB...)
        
        Returns:
            float: 1 birlik valyuta = N so'm
        """
        stmt = select(CurrencyModel).where(
            CurrencyModel.code == code,
            CurrencyModel.is_active == True
        ).order_by(CurrencyModel.date.desc()).limit(1)
        
        result = await db.execute(stmt)
        currency = result.scalar_one_or_none()
        
        if currency:
            # Nominal hisobga olish (masalan, 1 JPY = 77 so'm, lekin 10 IDR = 7 so'm)
            return currency.rate_uzs / currency.nominal if currency.nominal else currency.rate_uzs
        
        return None


# Singleton instance
currency_updater = CurrencyUpdater(load_all=True)
