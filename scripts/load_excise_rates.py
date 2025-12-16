import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.excise import ExciseRate


TOBACCO_EXCISE = [
    {
        "category": "tobacco",
        "product_name_ru": "Сигареты с фильтром",
        "product_name_uz": "Filtrli sigaretalar",
        "tnved_codes": "2402201000",
        "import_rate_specific": 330000,
        "import_rate_unit": "sum/1000pcs",
        "local_rate_specific": 300000,
        "local_rate_unit": "sum/1000pcs",
        "note": "Статья 289-1",
    },
    {
        "category": "tobacco", 
        "product_name_ru": "Сигареты без фильтра",
        "product_name_uz": "Filtrsiz sigaretalar",
        "tnved_codes": "2402209000",
        "import_rate_specific": 175000,
        "import_rate_unit": "sum/1000pcs",
        "local_rate_specific": 160000,
        "local_rate_unit": "sum/1000pcs",
        "note": "Статья 289-1",
    },
    {
        "category": "tobacco",
        "product_name_ru": "Сигары, сигариллы",
        "product_name_uz": "Sigaralar, sigarillalar",
        "tnved_codes": "2402100000",
        "import_rate_specific": 20000,
        "import_rate_unit": "sum/pcs",
        "local_rate_specific": 20000,
        "local_rate_unit": "sum/pcs",
        "note": "Статья 289-1",
    },
    {
        "category": "tobacco",
        "product_name_ru": "Табак курительный, кальянный табак",
        "product_name_uz": "Chekish tamakisi, qalyon tamakisi",
        "tnved_codes": "2403110000",
        "import_rate_specific": 600000,
        "import_rate_unit": "sum/kg",
        "local_rate_specific": 600000,
        "local_rate_unit": "sum/kg",
        "note": "Статья 289-1",
    },
    {
        "category": "tobacco",
        "product_name_ru": "Жидкость для электронных сигарет",
        "product_name_uz": "Elektron sigaret suyuqligi",
        "tnved_codes": "2403990009",
        "import_rate_specific": 2000,
        "import_rate_unit": "sum/ml",
        "local_rate_specific": 2000,
        "local_rate_unit": "sum/ml",
        "note": "Статья 289-1",
    },
    {
        "category": "tobacco",
        "product_name_ru": "Насвай",
        "product_name_uz": "Nasvoy",
        "tnved_codes": "2403990001",
        "import_rate_specific": 125000,
        "import_rate_unit": "sum/kg",
        "local_rate_specific": 125000,
        "local_rate_unit": "sum/kg",
        "note": "Статья 289-1",
    },
]

ALCOHOL_EXCISE = [
    {
        "category": "alcohol",
        "product_name_ru": "Спирт этиловый из пищевого сырья",
        "product_name_uz": "Oziq-ovqat xom ashyosidan etil spirti",
        "tnved_codes": "2207100000",
        "import_rate_specific": 15000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 15000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Спирт этиловый из непищевого сырья",
        "product_name_uz": "Nooziq-ovqat xom ashyosidan etil spirti",
        "tnved_codes": "2207200000",
        "import_rate_specific": 15000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 3300,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Водка, ликеро-водочные изделия, коньяк",
        "product_name_uz": "Aroq, aroq-liker mahsulotlari, konyak",
        "tnved_codes": "2208",
        "import_rate_specific": 76000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 44000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Вина натуральные виноградные",
        "product_name_uz": "Tabiiy uzum vinolari",
        "tnved_codes": "2204",
        "import_rate_specific": 14000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 5000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Вина виноградные крепленые, вермуты",
        "product_name_uz": "Mustahkamlangan uzum vinolari, vermutlar",
        "tnved_codes": "2204",
        "import_rate_specific": 25000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 10000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2, крепленые и вермуты",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Вина игристые, шампанское",
        "product_name_uz": "Ko'pikli vinolar, shampan vinosi",
        "tnved_codes": "2204100000",
        "import_rate_specific": 20000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 7000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Вина плодовые и плодово-ягодные",
        "product_name_uz": "Meva va meva-rezavorli vinolar",
        "tnved_codes": "2206",
        "import_rate_specific": 14000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 3500,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Пиво солодовое",
        "product_name_uz": "Salatli (solodli) pivo",
        "tnved_codes": "2203000000",
        "import_rate_specific": 6000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 2000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2",
    },
    {
        "category": "alcohol",
        "product_name_ru": "Напитки смешанные с содержанием пива",
        "product_name_uz": "Pivo tarkibli aralashma ichimliklar",
        "tnved_codes": "2206",
        "import_rate_specific": 6000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 4000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-2, с содержанием пива",
    },
]

PETROLEUM_OTHER_EXCISE = [
    {
        "category": "petroleum",
        "product_name_ru": "Бензин АИ-80 и ниже",
        "product_name_uz": "AI-80 va undan past benzin",
        "tnved_codes": "2710121100",
        "import_rate_specific": 340000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 340000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 375000 сум/тонна",
    },
    {
        "category": "petroleum",
        "product_name_ru": "Бензин выше АИ-80",
        "product_name_uz": "AI-80 dan yuqori benzin",
        "tnved_codes": "2710121500",
        "import_rate_specific": 550000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 550000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 600000 сум/тонна",
    },
    {
        "category": "petroleum",
        "product_name_ru": "Дизельное топливо",
        "product_name_uz": "Dizel yoqilg'isi",
        "tnved_codes": "2710192100",
        "import_rate_specific": 326000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 326000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 360000 сум/тонна",
    },
    {
        "category": "petroleum",
        "product_name_ru": "Газ сжиженный для автотранспорта",
        "product_name_uz": "Avtotransport uchun suyultirilgan gaz",
        "tnved_codes": "2711",
        "import_rate_specific": 148000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 148000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 164000 сум/тонна",
    },
    {
        "category": "petroleum",
        "product_name_ru": "Керосин авиационный",
        "product_name_uz": "Aviatsiya kerosini",
        "tnved_codes": "2710191100",
        "import_rate_specific": 148000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 148000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 164000 сум/тонна",
    },
    {
        "category": "petroleum",
        "product_name_ru": "Мазут",
        "product_name_uz": "Mazut",
        "tnved_codes": "2710196100",
        "import_rate_specific": 74000,
        "import_rate_unit": "sum/ton",
        "local_rate_specific": 74000,
        "local_rate_unit": "sum/ton",
        "note": "Статья 289-3. С 1 апреля 2025 года - 82000 сум/тонна",
    },
    # Shakar
    {
        "category": "sugar",
        "product_name_ru": "Сахар белый, сахар тростниковый",
        "product_name_uz": "Oq shakar, qamish shakari",
        "tnved_codes": "1701",
        "import_rate_percent": 20,
        "import_rate_unit": "percent",
        "note": "Статья 289-3",
    },
    # Ichimliklar
    {
        "category": "beverages",
        "product_name_ru": "Сладкие газированные напитки",
        "product_name_uz": "Shirin gazli ichimliklar",
        "tnved_codes": "2202",
        "import_rate_specific": 500,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 500,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-3",
    },
    {
        "category": "beverages",
        "product_name_ru": "Напитки энергетические безалкогольные",
        "product_name_uz": "Alkogolsiz energetik ichimliklar",
        "tnved_codes": "2202",
        "import_rate_specific": 2000,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 2000,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-3, энергетические напитки",
    },
    {
        "category": "beverages",
        "product_name_ru": "Соки, нектары, морсы",
        "product_name_uz": "Sharbatlar, nektarlar, morslar",
        "tnved_codes": "2009",
        "import_rate_specific": 500,
        "import_rate_unit": "sum/liter",
        "local_rate_specific": 500,
        "local_rate_unit": "sum/liter",
        "note": "Статья 289-3",
    },
]


async def load_excise_rates():    
    async with AsyncSessionLocal() as session:
        await session.execute(delete(ExciseRate))
        await session.commit()
        print("Eski aksiz stavkalari o'chirildi")
        
        all_excise = TOBACCO_EXCISE + ALCOHOL_EXCISE + PETROLEUM_OTHER_EXCISE
        
        loaded = 0
        for item in all_excise:
            excise = ExciseRate(
                category=item["category"],
                product_name_ru=item["product_name_ru"],
                product_name_uz=item.get("product_name_uz"),
                tnved_codes=item.get("tnved_codes"),
                import_rate_percent=item.get("import_rate_percent"),
                import_rate_specific=item.get("import_rate_specific"),
                import_rate_unit=item.get("import_rate_unit"),
                import_rate_min=item.get("import_rate_min"),
                local_rate_percent=item.get("local_rate_percent"),
                local_rate_specific=item.get("local_rate_specific"),
                local_rate_unit=item.get("local_rate_unit"),
                note=item.get("note"),
                is_active=True,
            )
            session.add(excise)
            loaded += 1
        
        await session.commit()
        print(f"✅ {loaded} ta aksiz stavkasi yuklandi")
        result = await session.execute(
            select(ExciseRate.category, ExciseRate.product_name_ru, ExciseRate.import_rate_specific, ExciseRate.import_rate_percent, ExciseRate.import_rate_unit)
        )
        
        print("\n📊 Yuklangan aksiz stavkalari:")
        print("-" * 80)
        current_category = None
        for row in result:
            if row.category != current_category:
                current_category = row.category
                print(f"\n[{current_category.upper()}]")
            
            if row.import_rate_percent:
                print(f"  - {row.product_name_ru[:50]}: {row.import_rate_percent}%")
            elif row.import_rate_specific:
                print(f"  - {row.product_name_ru[:50]}: {row.import_rate_specific:,.0f} {row.import_rate_unit}")


if __name__ == "__main__":
    asyncio.run(load_excise_rates())
