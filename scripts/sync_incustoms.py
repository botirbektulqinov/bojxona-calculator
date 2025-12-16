import asyncio
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete
from app.db.session import AsyncSessionLocal
from app.models.tnved import TNVedCode
from app.models.tariff import TariffRate

SUPABASE_URL = "https://zmnvdstrxrzxcdniaxmr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InptbnZkc3RyeHJ6eGNkbmlheG1yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM3OTkzMDMsImV4cCI6MjA3OTM3NTMwM30.tGAqUsyeNGS3EOl48Jl6Sf-wNizeDeJVRdrzzuGeckA"


class IncustomsSync:    
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        self.stats = {
            "total_fetched": 0,
            "inserted": 0,
            "updated": 0,
            "errors": []
        }
    
    async def fetch_tnved_items(self, offset: int = 0, limit: int = 1000) -> list:
        async with httpx.AsyncClient(timeout=60.0) as client:
            url = f"{SUPABASE_URL}/rest/v1/tnved_items"
            params = {
                "select": "*",
                "offset": offset,
                "limit": limit,
                "order": "code"
            }
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def fetch_all_items(self) -> list:
        all_items = []
        offset = 0
        limit = 1000
        
        print("incustoms.ai dan ma'lumotlar yuklanmoqda...")
        
        while True:
            items = await self.fetch_tnved_items(offset=offset, limit=limit)
            if not items:
                break
            all_items.extend(items)
            print(f"  Yuklandi: {len(all_items)} ta yozuv")
            offset += limit
        
        self.stats["total_fetched"] = len(all_items)
        print(f"Jami yuklandi: {len(all_items)} ta TNVED kod")
        return all_items
    
    async def sync_to_database(self, db: AsyncSession, items: list):        
        print("\nMahalliy baza tozalanmoqda...")
        await db.execute(delete(TariffRate))
        await db.execute(delete(TNVedCode))
        await db.commit()
        
        print("Yangi ma'lumotlar qo'shilmoqda...")
        
        for i, item in enumerate(items):
            try:
                code = item.get("code", "")
                if not code or len(code) < 2:
                    continue                
                tnved = TNVedCode(
                    code=code,
                    description=item.get("description") or "",
                    level=len(code),  
                    full_code=code
                )
                db.add(tnved)
                await db.flush()  
                duty_percent = item.get("duty_rate_rnb")
                if duty_percent is None:
                    duty_percent = item.get("duty_rate_non_rnb")
                if duty_percent is None:
                    duty_percent = 0.0                
                duty_specific = item.get("duty_specific_value")
                if duty_specific is None:
                    duty_specific = item.get("duty_rate_rnb_specific")
                
                specific_unit = item.get("duty_specific_per") or item.get("specific_rate_unit_name")
                
                tariff = TariffRate(
                    tnved_id=tnved.id,
                    import_duty_percent=float(item.get("duty_rate_rnb")) if item.get("duty_rate_rnb") is not None else None,
                    import_duty_percent_non_rnb=float(item.get("duty_rate_non_rnb")) if item.get("duty_rate_non_rnb") is not None else None,
                    import_duty_specific=float(item.get("duty_rate_rnb_specific") or item.get("duty_specific_value") or 0) if (item.get("duty_rate_rnb_specific") or item.get("duty_specific_value")) else None,
                    import_duty_specific_non_rnb=float(item.get("duty_rate_non_rnb_specific") or item.get("duty_specific_value") or 0) if (item.get("duty_rate_non_rnb_specific") or item.get("duty_specific_value")) else None,
                    specific_unit=specific_unit,
                    excise_percent=float(item.get("excise_value")) if item.get("excise_value") else None,
                    vat_percent=float(item.get("vat_rate") or item.get("vat") or 12.0),
                    source_url="https://incustoms.ai"
                )
                db.add(tariff)
                self.stats["inserted"] += 1
                
                if (i + 1) % 500 == 0:
                    await db.commit()
                    print(f"  Saqlandi: {i + 1} / {len(items)}")
                    
            except Exception as e:
                self.stats["errors"].append(f"{code}: {str(e)}")
                continue
        
        await db.commit()
        print(f"Jami saqlandi: {self.stats['inserted']} ta yozuv")
    
    async def sync(self):
        print("=" * 60)
        print("incustoms.ai dan sinxronizatsiya boshlanmoqda...")
        print("=" * 60)
        items = await self.fetch_all_items()
        
        if not items:
            print("Xato: Ma'lumotlar olinmadi!")
            return        
        async with AsyncSessionLocal() as db:
            await self.sync_to_database(db, items)        
        print("\n" + "=" * 70)
        print("✅ SINXRONIZATSIYA MUVAFFAQIYATLI YAKUNLANDI")
        print("=" * 70)
        print(f"📊 Manba: incustoms.ai (Supabase)")
        print(f"🔗 URL: https://incustoms.ai")
        print(f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📦 Statistika:")
        print(f"   • incustoms.ai dan yuklangan: {self.stats['total_fetched']} ta kod")
        print(f"   • Mahalliy bazaga saqlangan: {self.stats['inserted']} ta kod")
        print(f"   • Jami TN VED kodlar: {self.stats['total_fetched']}")
        print(f"\n✨ Tarif ma'lumotlari:")
        print(f"   • RNB stavkalari (MDH mamlakatlar)")
        print(f"   • Non-RNB stavkalari (boshqa mamlakatlar)")
        print(f"   • QQS va aksiz stavkalari")
        print(f"   • Spetsifik stavkalar (USD/kg)")
        if self.stats["errors"]:
            print(f"\n⚠️  Xatolar: {len(self.stats['errors'])}")
            for err in self.stats["errors"][:5]:
                print(f"   - {err}")
        print("\n" + "=" * 70)
        print("ℹ️  Ushbu ma'lumotlar incustoms.ai platformasi bilan sinxronlangan")
        print("=" * 70)


async def main():
    sync = IncustomsSync()
    await sync.sync()


if __name__ == "__main__":
    asyncio.run(main())
