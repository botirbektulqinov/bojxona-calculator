import asyncio
import sys
sys.path.insert(0, '/home/brave/Prog/bojxona-backend')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.parsers.lex_uz_parser import LexUzParser
from app.models.tariff import TariffRate
from app.models.tnved import TNVedCode


async def load_tariffs():    
    parser = LexUzParser()
    print("=" * 60)
    print("Lex.uz dan tarif ma'lumotlarini yuklash")
    print("=" * 60)
    print("\n1. Poshlina stavkalarini parse qilish...")
    duties = await parser.parse_duty_rates()
    print(f"   Topildi: {len(duties)} ta yozuv")
    
    with_percent = [d for d in duties if d.duty_percent is not None]
    with_specific = [d for d in duties if d.duty_specific is not None]
    print(f"   Foiz stavkasi: {len(with_percent)}")
    print(f"   Spetsifik stavka: {len(with_specific)}")    
    print("\n2. Bazaga yuklash...")
    
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM tariff_rates"))
        await db.commit()
        print("   Eski tariff_rates tozalandi")        
        tnved_result = await db.execute(text("SELECT code, id FROM tn_ved_codes"))
        existing_tnved = {row[0]: row[1] for row in tnved_result.fetchall()}
        print(f"   Mavjud TN VED kodlar: {len(existing_tnved)}")        
        added_tnved = 0
        added_tariffs = 0
        
        for duty in duties:
            code = duty.tnved_code
            if code not in existing_tnved:
                new_tnved = TNVedCode(
                    code=code,
                    description=duty.description or f"Kod {code}",
                    level=len(code)
                )
                db.add(new_tnved)
                await db.flush()
                existing_tnved[code] = new_tnved.id
                added_tnved += 1
            if duty.duty_percent is not None:
                tnved_id = existing_tnved.get(code)
                if tnved_id:
                    tariff_rate = TariffRate(
                        tnved_id=tnved_id,
                        import_duty_percent=duty.duty_percent,
                        import_duty_specific=duty.duty_specific,
                        specific_unit=duty.specific_unit,
                        excise_percent=duty.excise_percent,
                        excise_specific=duty.excise_specific,
                        vat_percent=12.0,  
                        source_url=duty.source_url
                    )
                    db.add(tariff_rate)
                    added_tariffs += 1
        
        await db.commit()
        print(f"   Qo'shilgan TN VED kodlar: {added_tnved}")
        print(f"   Qo'shilgan tariff stavkalar: {added_tariffs}")
    print("\n3. Yakuniy statistika:")
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM tn_ved_codes"))
        tnved_count = result.scalar()
        
        result = await db.execute(text("SELECT COUNT(*) FROM tariff_rates"))
        tariff_count = result.scalar()
        
        result = await db.execute(text("SELECT COUNT(*) FROM tariff_rates WHERE duty_specific IS NOT NULL"))
        specific_count = result.scalar()
        
        print(f"   TN VED kodlar: {tnved_count}")
        print(f"   Tariff stavkalar: {tariff_count}")
        print(f"   Spetsifik stavkalar: {specific_count}")
    
    print("\n" + "=" * 60)
    print("Yuklash tugadi!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(load_tariffs())
