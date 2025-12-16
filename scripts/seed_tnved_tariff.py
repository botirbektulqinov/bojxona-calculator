#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/home/brave/Prog/bojxona-backend')

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.tnved import TNVedCode
from app.models.tariff import TariffRate

TNVED_CODES = [
    # Avtomobillar
    {"code": "8703", "description": "Yengil avtomobillar va boshqa avtotransport vositalari", "level": 4},
    {"code": "87032110", "description": "Yengil avtomobillar, dvigatel hajmi 1000 sm3 gacha", "level": 8},
    {"code": "87032190", "description": "Boshqa avtomobillar, dvigatel hajmi 1000 sm3 gacha", "level": 8},
    {"code": "87032210", "description": "Avtomobillar, dvigatel hajmi 1000-1500 sm3", "level": 8},
    {"code": "87032290", "description": "Boshqa avtomobillar, dvigatel hajmi 1000-1500 sm3", "level": 8},
    {"code": "87032310", "description": "Avtomobillar, dvigatel hajmi 1500-3000 sm3", "level": 8},
    {"code": "87032390", "description": "Boshqa avtomobillar, dvigatel hajmi 1500-3000 sm3", "level": 8},
    {"code": "87032410", "description": "Avtomobillar, dvigatel hajmi 3000 sm3 dan yuqori", "level": 8},
    
    # Elektronika
    {"code": "8471", "description": "Avtomatik ma'lumotlarni qayta ishlash mashinalari (kompyuterlar)", "level": 4},
    {"code": "84713000", "description": "Portativ raqamli kompyuterlar (noutbuklar)", "level": 8},
    {"code": "84714100", "description": "Boshqa kompyuterlar bitta protsessor bilan", "level": 8},
    {"code": "84714900", "description": "Boshqa kompyuterlar bir nechta protsessor bilan", "level": 8},
    
    {"code": "8517", "description": "Telefonlar va aloqa uskunalari", "level": 4},
    {"code": "85171200", "description": "Smartfonlar", "level": 8},
    {"code": "85171300", "description": "Mobil telefonlar (smartfonsiz)", "level": 8},
    {"code": "85176200", "description": "Tarmoq uskunalari (routerlar)", "level": 8},
    
    # Maishiy texnika
    {"code": "8418", "description": "Muzlatgichlar va sovutgichlar", "level": 4},
    {"code": "84181000", "description": "Kombinirlangan muzlatgich-sovutgichlar", "level": 8},
    {"code": "84182100", "description": "Maishiy kompressor muzlatgichlar", "level": 8},
    
    {"code": "8450", "description": "Kir yuvish mashinalari", "level": 4},
    {"code": "84501100", "description": "To'liq avtomatik kir yuvish mashinalari", "level": 8},
    {"code": "84501200", "description": "Boshqa kir yuvish mashinalari", "level": 8},
    
    # Mebel
    {"code": "9403", "description": "Mebel va uning qismlari", "level": 4},
    {"code": "94031000", "description": "Ofis mebellari", "level": 8},
    {"code": "94032000", "description": "Metall mebel", "level": 8},
    {"code": "94033000", "description": "Yog'och ofis mebeli", "level": 8},
    {"code": "94034000", "description": "Oshxona mebeli", "level": 8},
    {"code": "94035000", "description": "Yotoqxona mebeli", "level": 8},
    
    # Kiyim-kechak
    {"code": "6203", "description": "Erkaklar kostyumlari va shim-ko'ylaklar", "level": 4},
    {"code": "62031100", "description": "Jun kostyumlar", "level": 8},
    {"code": "62031200", "description": "Sintetik kostyumlar", "level": 8},
    {"code": "62034100", "description": "Jun shimlar", "level": 8},
    {"code": "62034200", "description": "Paxta shimlar", "level": 8},
    
    {"code": "6204", "description": "Ayollar kostyumlari va ko'ylaklar", "level": 4},
    {"code": "64041100", "description": "Jun ayollar kostyumlari", "level": 8},
    {"code": "62042200", "description": "Paxta ayollar kostyumlari", "level": 8},
    
    # Oziq-ovqat
    {"code": "0201", "description": "Mol go'shti, yangi yoki sovutilgan", "level": 4},
    {"code": "02011000", "description": "Mol tushasi yoki yarim tushasi", "level": 8},
    {"code": "02012000", "description": "Suyakli mol go'shti", "level": 8},
    {"code": "02013000", "description": "Suyaksiz mol go'shti", "level": 8},
    
    {"code": "0207", "description": "Parranda go'shti", "level": 4},
    {"code": "02071100", "description": "Tovuq tushasi, yangi", "level": 8},
    {"code": "02071200", "description": "Tovuq tushasi, muzlatilgan", "level": 8},
    {"code": "02071300", "description": "Tovuq bo'laklari, yangi", "level": 8},
    {"code": "02071400", "description": "Tovuq bo'laklari, muzlatilgan", "level": 8},
    
    # Qurilish materiallari
    {"code": "6802", "description": "Tabiiy tosh, ishlov berilgan", "level": 4},
    {"code": "68021000", "description": "Tosh plitalar", "level": 8},
    {"code": "68022100", "description": "Marmor plitalar", "level": 8},
    {"code": "68022300", "description": "Granit plitalar", "level": 8},
    
    {"code": "7208", "description": "Po'lat yassiq prokat", "level": 4},
    {"code": "72081000", "description": "Rulonlardagi po'lat", "level": 8},
    {"code": "72082500", "description": "3mm dan qalin po'lat", "level": 8},
    
    # Kimyo mahsulotlari
    {"code": "3304", "description": "Kosmetika va parfyumeriya", "level": 4},
    {"code": "33041000", "description": "Lab bo'yoqlari", "level": 8},
    {"code": "33042000", "description": "Ko'z kosmetikasi", "level": 8},
    {"code": "33043000", "description": "Manikur va pedikur vositalari", "level": 8},
    
    # O'yinchoqlar
    {"code": "9503", "description": "O'yinchoqlar", "level": 4},
    {"code": "95030010", "description": "Elektr o'yinchoqlar", "level": 8},
    {"code": "95030021", "description": "Qo'g'irchoqlar", "level": 8},
    {"code": "95030041", "description": "Konstruktorlar", "level": 8},
]

# Tariff stavkalari (kodga qarab)
TARIFF_RATES = {
    # Avtomobillar - yuqori bojlar
    "8703": {"import_duty": 20, "excise": 15, "vat": 12},
    "87032110": {"import_duty": 30, "excise": 0, "vat": 12},
    "87032190": {"import_duty": 30, "excise": 0, "vat": 12},
    "87032210": {"import_duty": 30, "excise": 5, "vat": 12},
    "87032290": {"import_duty": 30, "excise": 5, "vat": 12},
    "87032310": {"import_duty": 30, "excise": 10, "vat": 12},
    "87032390": {"import_duty": 30, "excise": 10, "vat": 12},
    "87032410": {"import_duty": 30, "excise": 20, "vat": 12},
    
    # Elektronika - past bojlar
    "8471": {"import_duty": 0, "excise": 0, "vat": 12},
    "84713000": {"import_duty": 0, "excise": 0, "vat": 12},
    "84714100": {"import_duty": 0, "excise": 0, "vat": 12},
    "84714900": {"import_duty": 0, "excise": 0, "vat": 12},
    
    "8517": {"import_duty": 5, "excise": 0, "vat": 12},
    "85171200": {"import_duty": 5, "excise": 0, "vat": 12},
    "85171300": {"import_duty": 5, "excise": 0, "vat": 12},
    "85176200": {"import_duty": 0, "excise": 0, "vat": 12},
    
    # Maishiy texnika
    "8418": {"import_duty": 15, "excise": 0, "vat": 12},
    "84181000": {"import_duty": 15, "excise": 0, "vat": 12},
    "84182100": {"import_duty": 15, "excise": 0, "vat": 12},
    
    "8450": {"import_duty": 15, "excise": 0, "vat": 12},
    "84501100": {"import_duty": 15, "excise": 0, "vat": 12},
    "84501200": {"import_duty": 15, "excise": 0, "vat": 12},
    
    # Mebel
    "9403": {"import_duty": 20, "excise": 0, "vat": 12},
    "94031000": {"import_duty": 20, "excise": 0, "vat": 12},
    "94032000": {"import_duty": 20, "excise": 0, "vat": 12},
    "94033000": {"import_duty": 20, "excise": 0, "vat": 12},
    "94034000": {"import_duty": 20, "excise": 0, "vat": 12},
    "94035000": {"import_duty": 20, "excise": 0, "vat": 12},
    
    # Kiyim
    "6203": {"import_duty": 30, "excise": 0, "vat": 12},
    "62031100": {"import_duty": 30, "excise": 0, "vat": 12},
    "62031200": {"import_duty": 30, "excise": 0, "vat": 12},
    "62034100": {"import_duty": 30, "excise": 0, "vat": 12},
    "62034200": {"import_duty": 30, "excise": 0, "vat": 12},
    
    "6204": {"import_duty": 30, "excise": 0, "vat": 12},
    "64041100": {"import_duty": 30, "excise": 0, "vat": 12},
    "62042200": {"import_duty": 30, "excise": 0, "vat": 12},
    
    # Oziq-ovqat - past bojlar
    "0201": {"import_duty": 10, "excise": 0, "vat": 0},
    "02011000": {"import_duty": 10, "excise": 0, "vat": 0},
    "02012000": {"import_duty": 10, "excise": 0, "vat": 0},
    "02013000": {"import_duty": 10, "excise": 0, "vat": 0},
    
    "0207": {"import_duty": 10, "excise": 0, "vat": 0},
    "02071100": {"import_duty": 10, "excise": 0, "vat": 0},
    "02071200": {"import_duty": 10, "excise": 0, "vat": 0},
    "02071300": {"import_duty": 10, "excise": 0, "vat": 0},
    "02071400": {"import_duty": 10, "excise": 0, "vat": 0},
    
    # Qurilish materiallari
    "6802": {"import_duty": 15, "excise": 0, "vat": 12},
    "68021000": {"import_duty": 15, "excise": 0, "vat": 12},
    "68022100": {"import_duty": 15, "excise": 0, "vat": 12},
    "68022300": {"import_duty": 15, "excise": 0, "vat": 12},
    
    "7208": {"import_duty": 5, "excise": 0, "vat": 12},
    "72081000": {"import_duty": 5, "excise": 0, "vat": 12},
    "72082500": {"import_duty": 5, "excise": 0, "vat": 12},
    
    # Kosmetika
    "3304": {"import_duty": 20, "excise": 0, "vat": 12},
    "33041000": {"import_duty": 20, "excise": 0, "vat": 12},
    "33042000": {"import_duty": 20, "excise": 0, "vat": 12},
    "33043000": {"import_duty": 20, "excise": 0, "vat": 12},
    
    # O'yinchoqlar
    "9503": {"import_duty": 15, "excise": 0, "vat": 12},
    "95030010": {"import_duty": 15, "excise": 0, "vat": 12},
    "95030021": {"import_duty": 15, "excise": 0, "vat": 12},
    "95030041": {"import_duty": 15, "excise": 0, "vat": 12},
}


async def seed_tnved_and_tariffs():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(TNVedCode))
        existing_codes = {code.code: code for code in result.scalars().all()}
        
        print(f"Mavjud TNVED kodlar soni: {len(existing_codes)}")
        
        added_tnved = 0
        added_tariff = 0
        
        for tnved_data in TNVED_CODES:
            code = tnved_data["code"]
            
            if code in existing_codes:
                tnved_obj = existing_codes[code]
                print(f"  Mavjud: {code}")
            else:
                tnved_obj = TNVedCode(
                    code=code,
                    full_code=code,
                    description=tnved_data["description"],
                    level=tnved_data["level"]
                )
                db.add(tnved_obj)
                await db.flush()  
                added_tnved += 1
                print(f"  Qo'shildi TNVED: {code} - {tnved_data['description'][:40]}")
            
            if code in TARIFF_RATES:
                tariff_result = await db.execute(
                    select(TariffRate).filter(TariffRate.tnved_id == tnved_obj.id)
                )
                existing_tariff = tariff_result.scalars().first()
                
                if not existing_tariff:
                    rates = TARIFF_RATES[code]
                    tariff = TariffRate(
                        tnved_id=tnved_obj.id,
                        import_duty_percent=rates["import_duty"],
                        excise_percent=rates["excise"],
                        vat_percent=rates["vat"]
                    )
                    db.add(tariff)
                    added_tariff += 1
                    print(f"    Tariff: {rates['import_duty']}% boj, {rates['excise']}% aksiz, {rates['vat']}% QQS")
        
        await db.commit()
        
        print(f"\n=== Natija ===")
        print(f"Qo'shilgan TNVED kodlar: {added_tnved}")
        print(f"Qo'shilgan Tarifflar: {added_tariff}")
        result = await db.execute(select(TNVedCode))
        total_tnved = len(result.scalars().all())
        
        result = await db.execute(select(TariffRate))
        total_tariff = len(result.scalars().all())
        
        print(f"\nJami TNVED kodlar: {total_tnved}")
        print(f"Jami Tarifflar: {total_tariff}")


if __name__ == "__main__":
    asyncio.run(seed_tnved_and_tariffs())
