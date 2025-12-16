"""
Lex.uz saytidan bojxona stavkalarini parse qilish.
Manbalar:
- https://lex.uz/docs/3802366 - Import poshlinasi
- https://lex.uz/docs/6718877 - Aksiz
- https://lex.uz/docs/4911947 - Erkin savdo mamlakatlar
"""

import httpx
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tariff import tariff
from app.crud.tnved import tnved
from app.schemas.tariff import TariffRateCreate


@dataclass
class ParsedTariff:
    """Parse qilingan tarif ma'lumoti"""
    tnved_code: str
    description: Optional[str]
    duty_percent: Optional[float]
    duty_specific: Optional[float]
    specific_unit: Optional[str]
    excise_percent: Optional[float]
    excise_specific: Optional[float]
    source_url: str


class LexUzParser:
    """Lex.uz saytidan ma'lumotlarni parse qilish"""
    
    DUTY_URL = "https://lex.uz/docs/3802366"
    EXCISE_URL = "https://lex.uz/docs/6718877"
    FREE_TRADE_URL = "https://lex.uz/docs/4911947"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Sahifani olish"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                if response.status_code == 200:
                    return response.text
                print(f"Failed to fetch {url}: {response.status_code}")
                return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
    
    def parse_duty_table(self, html_content: str) -> List[ParsedTariff]:
        """
        Poshlina jadvalini parse qilish.
        Jadval strukturasi:
        | TN VED kodi | Tovar tavsifi | Stavka (% yoki $) |
        
        Stavka formatlari:
        - "0" yoki "5" yoki "10" - oddiy foiz
        - "15, но не менее 0,3 доллара США за килограмм" - kombinatsiya
        - "30 + 3 доллара США за куб. см." - kombinatsiya
        """
        soup = BeautifulSoup(html_content, 'lxml')
        results = []
        
        # Jadvallarni topish
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:  # Kamida 3 ta ustun kerak: kod, tavsif, stavka
                    continue
                
                # Birinchi ustun - kod
                code_text = cells[0].get_text(strip=True)
                # Vergul yoki bo'shliq bilan ajratilgan bir nechta kodlarni olish
                code_parts = re.findall(r'\d{4,10}', code_text)
                if not code_parts:
                    continue
                
                # Asosiy kodni olish (birinchi to'liq kod)
                code_clean = code_parts[0]
                
                # Kodmi tekshirish (kamida 4 ta raqam - TN VED format)
                if len(code_clean) < 4:
                    continue
                
                # Ikkinchi ustun - tavsif
                description = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                
                # Uchinchi ustun - stavka
                rate_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                # Stavkani parse qilish
                duty_percent, duty_specific, specific_unit = self.parse_rate_from_text(rate_text)
                
                # Agar % belgisi yo'q bo'lsa, oddiy son sifatida tekshirish
                if duty_percent is None and rate_text:
                    # "0", "5", "10", "20" kabi oddiy sonlarni tekshirish
                    simple_match = re.match(r'^(\d+(?:[.,]\d+)?)\s*(?:,|$|\s|\*)', rate_text)
                    if simple_match:
                        duty_percent = float(simple_match.group(1).replace(',', '.'))
                
                if code_clean and (duty_percent is not None or description):
                    results.append(ParsedTariff(
                        tnved_code=code_clean,
                        description=description if description else None,
                        duty_percent=duty_percent,
                        duty_specific=duty_specific,
                        specific_unit=specific_unit,
                        excise_percent=None,
                        excise_specific=None,
                        source_url=self.DUTY_URL
                    ))
        
        return results
    
    def parse_rate_from_text(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Stavkani matndan ajratib olish.
        Qaytaradi: (foiz_stavka, spetsifik_stavka, birlik)
        
        Misollar:
        - "0" yoki "15" -> (15.0, None, None)
        - "15%" -> (15.0, None, None)
        - "0.5 долларов США за кг" -> (None, 0.5, "kg")
        - "20, но не менее 0,3 доллара США за килограмм" -> (20.0, 0.3, "kg")
        - "30 + 3 доллара США за куб. см." -> (30.0, 3.0, "cm3")
        """
        if not text:
            return None, None, None
            
        percent_rate = None
        specific_rate = None
        unit = None
        
        # Foiz stavka - boshida yoki % bilan
        # "20, но не менее" yoki "30 + 3" formatida
        percent_match = re.search(r'^(\d+(?:[.,]\d+)?)\s*(?:%|,|\s|$|\+)', text)
        if percent_match:
            percent_rate = float(percent_match.group(1).replace(',', '.'))
        
        # Agar % belgisi aniq bo'lsa
        if percent_rate is None:
            explicit_percent = re.search(r'(\d+(?:[.,]\d+)?)\s*%', text)
            if explicit_percent:
                percent_rate = float(explicit_percent.group(1).replace(',', '.'))
        
        # Spetsifik stavka - "не менее X долларов" yoki "+ X долларов"
        # Format: "0,3 доллара США за килограмм" yoki "3 долларов США за штуку"
        specific_patterns = [
            r'(?:не менее|менее)\s+(\d+(?:[.,]\d+)?)\s*(?:доллар|долл|\$)',
            r'\+\s*(\d+(?:[.,]\d+)?)\s*(?:доллар|долл|\$)',
            r'(\d+(?:[.,]\d+)?)\s*(?:доллар|долл|\$)\s*(?:США\s+)?за'
        ]
        
        for pattern in specific_patterns:
            specific_match = re.search(pattern, text, re.IGNORECASE)
            if specific_match:
                specific_rate = float(specific_match.group(1).replace(',', '.'))
                break
        
        # Birlik qidirish - "за килограмм", "за штуку", "за литр"
        unit_pattern = r'за\s+(?:каждый\s+)?(\w+(?:\.\s*\w+)?)'
        unit_match = re.search(unit_pattern, text, re.IGNORECASE)
        if unit_match:
            raw_unit = unit_match.group(1).lower().strip()
            # Birlikni standartlashtirish
            unit_map = {
                'килограмм': 'kg', 'кг': 'kg',
                'штуку': 'pcs', 'шт': 'pcs', 'штука': 'pcs',
                'литр': 'l', 'л': 'l',
                'куб': 'cm3', 'см': 'cm3',  # "куб. см."
                'пару': 'pair', 'пар': 'pair',
                'метр': 'm',
            }
            unit = unit_map.get(raw_unit, raw_unit)
        
        return percent_rate, specific_rate, unit
    
    async def parse_duty_rates(self) -> List[ParsedTariff]:
        """Poshlina stavkalarini olish va parse qilish"""
        html = await self.fetch_page(self.DUTY_URL)
        if not html:
            return []
        return self.parse_duty_table(html)
    
    async def parse_excise_rates(self) -> List[ParsedTariff]:
        """Aksiz stavkalarini olish va parse qilish"""
        html = await self.fetch_page(self.EXCISE_URL)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        results = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                code_text = cells[0].get_text(strip=True)
                code_clean = re.sub(r'[^\d]', '', code_text)
                
                if len(code_clean) < 4:  # Aksiz odatda aniq kodlar uchun
                    continue
                
                # Aksiz stavkasini qidirish
                excise_percent = None
                for cell in cells[1:]:
                    cell_text = cell.get_text(strip=True)
                    percent_match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', cell_text)
                    if percent_match:
                        excise_percent = float(percent_match.group(1).replace(',', '.'))
                        break
                
                if code_clean and excise_percent is not None:
                    results.append(ParsedTariff(
                        tnved_code=code_clean,
                        description=None,
                        duty_percent=None,
                        duty_specific=None,
                        specific_unit=None,
                        excise_percent=excise_percent,
                        excise_specific=None,
                        source_url=self.EXCISE_URL
                    ))
        
        return results
    
    async def save_tariffs_to_db(self, db: AsyncSession, tariffs: List[ParsedTariff]):
        """Parse qilingan tariflarni DB ga saqlash"""
        saved_count = 0
        error_count = 0
        
        for t in tariffs:
            try:
                # TNVED kodini topish
                tnved_obj = await tnved.get_by_code(db, code=t.tnved_code)
                if not tnved_obj:
                    # Kod topilmadi, skip
                    continue
                
                # Mavjud tarifni tekshirish
                existing = await tariff.get_by_tnved_id(db, tnved_id=tnved_obj.id)
                
                tariff_data = TariffRateCreate(
                    tnved_id=tnved_obj.id,
                    import_duty_percent=t.duty_percent,
                    import_duty_specific=t.duty_specific,
                    specific_unit=t.specific_unit,
                    excise_percent=t.excise_percent,
                    excise_specific=t.excise_specific,
                    vat_percent=12.0,  # O'zbekistonda standart QQS
                    source_url=t.source_url
                )
                
                if existing:
                    # Mavjud bo'lsa yangilash
                    await tariff.update(db, db_obj=existing, obj_in=tariff_data)
                else:
                    # Yangi yaratish
                    await tariff.create(db, obj_in=tariff_data)
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving tariff for {t.tnved_code}: {e}")
                error_count += 1
        
        return saved_count, error_count
    
    async def update_all(self, db: AsyncSession):
        """Barcha stavkalarni yangilash"""
        print("Parsing duty rates from lex.uz...")
        duty_tariffs = await self.parse_duty_rates()
        print(f"Found {len(duty_tariffs)} duty entries")
        
        print("Parsing excise rates from lex.uz...")
        excise_tariffs = await self.parse_excise_rates()
        print(f"Found {len(excise_tariffs)} excise entries")
        
        # Birlashtiramiz - bir xil kodlar uchun
        combined = {}
        
        for t in duty_tariffs:
            combined[t.tnved_code] = t
        
        for t in excise_tariffs:
            if t.tnved_code in combined:
                # Aksiz qo'shamiz
                combined[t.tnved_code].excise_percent = t.excise_percent
            else:
                combined[t.tnved_code] = t
        
        print(f"Saving {len(combined)} tariffs to database...")
        saved, errors = await self.save_tariffs_to_db(db, list(combined.values()))
        print(f"Saved: {saved}, Errors: {errors}")
        
        return saved, errors


# CLI uchun
async def main():
    """Parser'ni ishga tushirish"""
    from app.db.session import async_session
    
    parser = LexUzParser()
    
    async with async_session() as db:
        await parser.update_all(db)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
