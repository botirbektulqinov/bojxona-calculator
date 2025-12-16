"""
Bojxona to'lovlarini hisoblash xizmati.
TZ ga muvofiq barcha turdagi to'lovlarni hisoblaydi.

Hisoblash tartibi:
1. Bojxona qiymati (TS) = Tovar narxi + Yetkazib berish + Sug'urta
2. Bojxona rasmiylash yig'imi = BRV asosida yoki % 
3. Import bojxona poshlinasi = TS * Stavka (yoki spetsifik stavka)
4. Aksiz = (TS + Poshlina) * Aksiz stavkasi
5. QQS = (TS + Poshlina + Aksiz) * 12%
6. Utilizatsiya yig'imi (avtomobillar uchun)
7. Jami = Yig'im + Poshlina + Aksiz + QQS + Utilizatsiya

Maxsus holatlar:
- Erkin savdo zonasi mamlakatlar (ST-1 sertifikat bilan) - poshlina 0%
- Noma'lum mamlakat - poshlina 2x stavka
- Imtiyozlar - turli chegirmalar
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import date
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tnved import tnved
from app.crud.tariff import tariff
from app.crud.currency import currency
from app.crud.country import free_trade_country
from app.crud.benefit import tariff_benefit, customs_fee_rate, brv_rate
from app.crud.utilization import utilization_fee
from app.crud.excise import excise as excise_crud


class DutyRateType(str, Enum):
    """Poshlina stavka turi"""
    RNB = "rnb"  # Eng qulay tarif mamlakatlar - MDH davlatlari
    NON_RNB = "non_rnb"  # Boshqa mamlakatlar (yuqori stavka)
    FREE_TRADE = "free_trade"  # Erkin savdo (0%)
    DOUBLE = "double"  # Noma'lum mamlakat (2x stavka)
    PREFERENTIAL = "preferential"  # Imtiyozli

RNB_COUNTRIES = {
    "RU",  # Rossiya
    "KZ",  # Qozog'iston
    "KG",  # Qirg'iziston
    "TJ",  # Tojikiston
    "BY",  # Belarusiya
    "AM",  # Armaniston
    "AZ",  # Ozarbayjon
    "MD",  # Moldova
    "UA",  # Ukraina
    "GE",  # Gruziya
    "TM",  # Turkmaniston
}


@dataclass
class CalculationInput:
    """Hisoblash uchun kirish ma'lumotlari"""
    tnved_code: str
    price: float  # Tovar narxi (invoys)
    currency_code: str  # Valyuta kodi (USD, EUR, etc)
    weight_kg: float  # Vazn (kg)
    quantity: Optional[int] = None  # Miqdor (dona)
    country_origin: str = "XX"  # Kelib chiqish mamlakatsi (ISO kod)
    has_origin_certificate: bool = False  # ST-1 sertifikati bormi
    delivery_cost: float = 0.0  # Yetkazib berish narxi
    insurance_cost: float = 0.0  # Sug'urta narxi
    
    # Avtomobillar uchun qo'shimcha
    engine_volume_cc: Optional[int] = None  # Dvigatel hajmi (sm³)
    vehicle_age_years: Optional[int] = None  # Avtomobil yoshi


@dataclass
class PaymentItem:
    """Bitta to'lov turi"""
    name: str  # To'lov nomi
    name_uz: str  # O'zbekcha nomi
    base: float  # Hisoblash bazasi (UZS)
    rate: Optional[float]  # Stavka (% yoki spetsifik)
    rate_type: str  # 'percent', 'fixed', 'specific', 'brv'
    amount: float  # To'lov summasi (UZS)
    note: Optional[str] = None  # Izoh


@dataclass
class CalculationResult:
    """Hisoblash natijasi"""
    # Asosiy qiymatlar
    customs_value_uzs: float  # Bojxona qiymati (UZS)
    customs_value_usd: float  # Bojxona qiymati (USD)
    
    # To'lovlar
    payments: List[PaymentItem]
    
    # Jami
    total_uzs: float
    total_usd: float
    
    # Qo'shimcha ma'lumot
    effective_rate_percent: float  # Effektiv stavka (%)
    exchange_rate: float  # Valyuta kursi
    duty_rate_type: DutyRateType  # Poshlina stavka turi
    
    # Tafsilotlar
    details: Dict[str, Any]
    
    # Xatolar/ogohlantirishlar
    warnings: List[str]


class CustomsCalculator:
    """Bojxona to'lovlari kalkulyatori"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.warnings: List[str] = []
    
    async def calculate(self, input_data: CalculationInput) -> CalculationResult:
        """Asosiy hisoblash funksiyasi"""
        self.warnings = []
        payments: List[PaymentItem] = []
        
        # 1. TNVED kodni tekshirish va tarif olish
        code_obj = await tnved.get_by_code(self.db, code=input_data.tnved_code)
        if not code_obj:
            raise ValueError(f"TNVED kod topilmadi: {input_data.tnved_code}")
        
        # Avval aniq kod uchun tarif qidirish
        tariff_obj = await tariff.get_by_tnved_id(self.db, tnved_id=code_obj.id)
        
        # Agar topilmasa, shu kod bilan boshlanadigan kodlardan tarif olish
        if not tariff_obj:
            tariff_obj = await tariff.get_by_code_prefix(self.db, code=input_data.tnved_code)
            if tariff_obj:
                self.warnings.append(f"Aniq tarif topilmadi, {input_data.tnved_code}* bo'yicha tarif ishlatilmoqda")
            else:
                # TARIF TOPILMASA - XATO QAYTARISH (standart qiymat yo'q!)
                raise ValueError(
                    f"Lex.uz bazasida '{input_data.tnved_code}' kodi uchun tarif mavjud emas. "
                    f"Faqat rasmiy lex.uz ma'lumotlari bilan ishlash mumkin."
                )
        
        # 2. Valyuta kursini olish
        exchange_rate = await self._get_exchange_rate(input_data.currency_code)
        usd_rate = await self._get_exchange_rate("USD")
        
        # 3. Bojxona qiymatini hisoblash
        # TS = Narx + Yetkazib berish + Sug'urta
        price_uzs = input_data.price * exchange_rate
        delivery_uzs = input_data.delivery_cost * exchange_rate
        insurance_uzs = input_data.insurance_cost * exchange_rate
        
        customs_value_uzs = price_uzs + delivery_uzs + insurance_uzs
        customs_value_usd = customs_value_uzs / usd_rate if usd_rate > 0 else 0
        
        # 4. Poshlina stavka turini aniqlash
        duty_rate_type = await self._determine_duty_rate_type(
            input_data.country_origin,
            input_data.has_origin_certificate
        )
        
        # 5. Bojxona rasmiylash yig'imi
        customs_fee = await self._calculate_customs_fee(customs_value_uzs, customs_value_usd)
        payments.append(customs_fee)
        
        # 6. Import poshlina
        import_duty = await self._calculate_import_duty(
            customs_value_uzs=customs_value_uzs,
            weight_kg=input_data.weight_kg,
            tariff_obj=tariff_obj,
            duty_rate_type=duty_rate_type,
            usd_rate=usd_rate
        )
        payments.append(import_duty)
        
        # 7. Aksiz
        excise = await self._calculate_excise(
            customs_value_uzs=customs_value_uzs,
            import_duty_amount=import_duty.amount,
            tariff_obj=tariff_obj,
            tnved_code=input_data.tnved_code,
            weight_kg=input_data.weight_kg,
            quantity=input_data.quantity
        )
        payments.append(excise)
        
        # 8. QQS (VAT)
        vat = await self._calculate_vat(
            customs_value_uzs=customs_value_uzs,
            import_duty_amount=import_duty.amount,
            excise_amount=excise.amount,
            tariff_obj=tariff_obj
        )
        payments.append(vat)
        
        # 9. Utilizatsiya yig'imi (agar kerak bo'lsa)
        util_fee = await self._calculate_utilization_fee(
            tnved_code=input_data.tnved_code,
            engine_volume_cc=input_data.engine_volume_cc,
            vehicle_age_years=input_data.vehicle_age_years
        )
        if util_fee:
            payments.append(util_fee)
        
        # 10. Jami
        total_uzs = sum(p.amount for p in payments)
        total_usd = total_uzs / usd_rate if usd_rate > 0 else 0
        
        # Effektiv stavka
        effective_rate = (total_uzs / customs_value_uzs * 100) if customs_value_uzs > 0 else 0
        
        return CalculationResult(
            customs_value_uzs=customs_value_uzs,
            customs_value_usd=customs_value_usd,
            payments=payments,
            total_uzs=total_uzs,
            total_usd=total_usd,
            effective_rate_percent=round(effective_rate, 2),
            exchange_rate=exchange_rate,
            duty_rate_type=duty_rate_type,
            details={
                "tnved_code": input_data.tnved_code,
                "tnved_description": code_obj.description,
                "country_origin": input_data.country_origin,
                "has_certificate": input_data.has_origin_certificate,
                "tariff_duty_percent": tariff_obj.import_duty_percent if tariff_obj else None,
                "tariff_excise_percent": tariff_obj.excise_percent if tariff_obj else None,
                "tariff_vat_percent": tariff_obj.vat_percent if tariff_obj else 12.0,
            },
            warnings=self.warnings
        )
    
    async def _get_exchange_rate(self, currency_code: str) -> float:
        """Valyuta kursini olish"""
        if currency_code == "UZS":
            return 1.0
        
        # Bugungi kurs
        curr_obj = await currency.get_by_code_and_date(
            self.db, code=currency_code, date_obj=date.today()
        )
        
        if curr_obj:
            return float(curr_obj.rate_uzs)
        
        # Bugungi topilmasa, so'nggi kursni olish
        rates = await currency.get_latest_rates(self.db)
        found = next((r for r in rates if r.code == currency_code), None)
        
        if found:
            self.warnings.append(f"Bugungi {currency_code} kursi topilmadi, so'nggi kurs ishlatilmoqda")
            return float(found.rate_uzs)
        
        raise ValueError(f"Valyuta kursi topilmadi: {currency_code}")
    
    async def _determine_duty_rate_type(
        self, 
        country_code: str, 
        has_certificate: bool
    ) -> DutyRateType:
        """Poshlina stavka turini aniqlash"""
        
        # Noma'lum mamlakat - 2x stavka
        if country_code == "XX" or not country_code:
            return DutyRateType.DOUBLE
        
        # Erkin savdo zonasi tekshiruvi
        is_free_trade = await free_trade_country.is_free_trade(
            self.db, country_code=country_code
        )
        
        if is_free_trade and has_certificate:
            return DutyRateType.FREE_TRADE
        elif is_free_trade and not has_certificate:
            self.warnings.append(
                f"{country_code} erkin savdo zonasida, lekin sertifikat yo'q - standart stavka qo'llaniladi"
            )
        
        # RNB (MDH) mamlakatlar tekshiruvi
        if country_code.upper() in RNB_COUNTRIES:
            return DutyRateType.RNB
        
        # Boshqa mamlakatlar - NON_RNB (yuqori stavka)
        return DutyRateType.NON_RNB
    
    async def _calculate_customs_fee(self, customs_value_uzs: float, customs_value_usd: float) -> PaymentItem:
        """
        Bojxona rasmiylash yig'imini hisoblash.
        
        O'zbekiston bojxona kodeksiga muvofiq (TP-55),
        bojxona rasmiylash yig'imi BRV asosida hisoblanadi:
        
        | Bojxona qiymati (USD)   | BRV koeffitsienti |
        |-------------------------|-------------------|
        | $1,000 gacha            | 0.3 BRV           |
        | $1,000 - $5,000         | 0.5 BRV           |
        | $5,000 - $10,000        | 1.0 BRV           |
        | $10,000 - $20,000       | 1.5 BRV           |
        | $20,000 - $50,000       | 3.0 BRV           |
        | $50,000 - $100,000      | 5.0 BRV           |
        | $100,000 dan yuqori     | 10.0 BRV          |
        """
        
        # BRV qiymatini olish
        brv_obj = await brv_rate.get_current(self.db)
        brv_amount = brv_obj.amount if brv_obj else 412000.0  # 2025 yil uchun default
        
        # BRV koeffitsientini aniqlash
        if customs_value_usd <= 1000:
            brv_coefficient = 0.3
        elif customs_value_usd <= 5000:
            brv_coefficient = 0.5
        elif customs_value_usd <= 10000:
            brv_coefficient = 1.0
        elif customs_value_usd <= 20000:
            brv_coefficient = 1.5
        elif customs_value_usd <= 50000:
            brv_coefficient = 3.0
        elif customs_value_usd <= 100000:
            brv_coefficient = 5.0
        else:
            brv_coefficient = 10.0
        
        amount = brv_amount * brv_coefficient
        
        return PaymentItem(
            name="Customs Fee",
            name_uz="Bojxona rasmiylash yig'imi",
            base=brv_amount,
            rate=brv_coefficient,
            rate_type="brv",
            amount=amount,
            note=f"BRV x {brv_coefficient} (TP-55)"
        )
    
    async def _calculate_import_duty(
        self,
        customs_value_uzs: float,
        weight_kg: float,
        tariff_obj,
        duty_rate_type: DutyRateType,
        usd_rate: float
    ) -> PaymentItem:
        """Import poshlinasini hisoblash"""
        
        # Erkin savdo - 0%
        if duty_rate_type == DutyRateType.FREE_TRADE:
            return PaymentItem(
                name="Import Duty",
                name_uz="Import bojxona poshlinasi",
                base=customs_value_uzs,
                rate=0,
                rate_type="percent",
                amount=0,
                note="Erkin savdo zonasi (ST-1 sertifikat)"
            )
        
        # Tarif ma'lumoti yo'q
        if not tariff_obj:
            return PaymentItem(
                name="Import Duty",
                name_uz="Import bojxona poshlinasi",
                base=customs_value_uzs,
                rate=None,
                rate_type="unknown",
                amount=0,
                note="Tarif ma'lumoti topilmadi"
            )
        
        # RNB yoki non-RNB stavka tanlash
        if duty_rate_type == DutyRateType.RNB:
            # RNB (MDH) mamlakatlari uchun import_duty_percent
            duty_percent = tariff_obj.import_duty_percent
            duty_specific = tariff_obj.import_duty_specific
            rate_note = "RNB stavka (MDH)"
        elif duty_rate_type == DutyRateType.DOUBLE:
            # Noma'lum mamlakat - 2x stavka
            duty_percent = (tariff_obj.import_duty_percent or 0) * 2
            duty_specific = (tariff_obj.import_duty_specific or 0) * 2
            rate_note = "Noma'lum mamlakat (2x stavka)"
        else:
            # NON_RNB - Boshqa mamlakatlar uchun import_duty_percent_non_rnb
            duty_percent = getattr(tariff_obj, 'import_duty_percent_non_rnb', None)
            duty_specific = getattr(tariff_obj, 'import_duty_specific_non_rnb', None)
            
            # Agar non_rnb qiymati yo'q bo'lsa, RNB qiymatini 2x qilish
            if duty_percent is None:
                duty_percent = (tariff_obj.import_duty_percent or 0) * 2
            if duty_specific is None:
                duty_specific = (tariff_obj.import_duty_specific or 0) * 2 if tariff_obj.import_duty_specific else None
                
            rate_note = "Non-RNB stavka"
        
        duty_percent = duty_percent or 0
        
        # Advalor (foizli) hisoblash
        advalorem_duty = customs_value_uzs * (float(duty_percent) / 100)
        
        # Spetsifik stavka (agar bor bo'lsa)
        specific_duty = 0.0
        if duty_specific:
            # Spetsifik stavka odatda USD/kg da
            specific_duty = (float(duty_specific) * usd_rate) * weight_kg
        
        # Qaysi katta bo'lsa, shuni olish
        if specific_duty > advalorem_duty and specific_duty > 0:
            return PaymentItem(
                name="Import Duty",
                name_uz="Import bojxona poshlinasi",
                base=weight_kg,
                rate=float(duty_specific),
                rate_type="specific",
                amount=specific_duty,
                note=f"Spetsifik stavka (${duty_specific}/kg) - {rate_note}"
            )
        
        return PaymentItem(
            name="Import Duty",
            name_uz="Import bojxona poshlinasi",
            base=customs_value_uzs,
            rate=float(duty_percent),
            rate_type="percent",
            amount=advalorem_duty,
            note=rate_note
        )
    
    async def _calculate_excise(
        self,
        customs_value_uzs: float,
        import_duty_amount: float,
        tariff_obj,
        tnved_code: str,
        weight_kg: float,
        quantity: Optional[int]
    ) -> PaymentItem:
        """
        Aksiz soliqni hisoblash.
        
        Aksiz ikki xil usulda hisoblanishi mumkin:
        1. Foizli (advalor) - (TS + Poshlina) * %
        2. Spetsifik - birlik uchun belgilangan summa (sum/litr, sum/kg, sum/1000dona)
        """
        
        excise_base = customs_value_uzs + import_duty_amount
        
        # 1. Avval excise_rates jadvalidan tekshiramiz (yangi sistema)
        excise_rate_obj = await excise_crud.get_by_tnved_code(self.db, tnved_code)
        
        if excise_rate_obj:
            # Spetsifik stavka (absolyut summa)
            if excise_rate_obj.import_rate_specific:
                specific_rate = excise_rate_obj.import_rate_specific
                unit = excise_rate_obj.import_rate_unit or ""
                
                # Birlikka qarab hisoblash
                if "1000pcs" in unit:
                    # 1000 dona uchun - miqdor kerak
                    qty = quantity or 1
                    amount = (qty / 1000) * specific_rate
                    note = f"{specific_rate:,.0f} so'm / 1000 dona"
                elif "pcs" in unit:
                    # Dona uchun
                    qty = quantity or 1
                    amount = qty * specific_rate
                    note = f"{specific_rate:,.0f} so'm / dona"
                elif "liter" in unit:
                    # Litr uchun - og'irlikdan taxminiy hisoblash (1 litr ≈ 1 kg)
                    liters = weight_kg  # Taxminan
                    amount = liters * specific_rate
                    note = f"{specific_rate:,.0f} so'm / litr"
                elif "kg" in unit:
                    # Kg uchun
                    amount = weight_kg * specific_rate
                    note = f"{specific_rate:,.0f} so'm / kg"
                elif "ton" in unit:
                    # Tonna uchun
                    tons = weight_kg / 1000
                    amount = tons * specific_rate
                    note = f"{specific_rate:,.0f} so'm / tonna"
                elif "ml" in unit:
                    # Millilitr uchun (elektron sigaret suyuqligi)
                    ml = weight_kg * 1000  # 1 kg ≈ 1000 ml taxminan
                    amount = ml * specific_rate
                    note = f"{specific_rate:,.0f} so'm / ml"
                else:
                    # Noma'lum birlik - og'irlik bo'yicha
                    amount = weight_kg * specific_rate
                    note = f"{specific_rate:,.0f} so'm (spetsifik)"
                
                return PaymentItem(
                    name="Excise Tax",
                    name_uz="Aksiz solig'i",
                    base=weight_kg if "kg" in unit or "ton" in unit else (quantity or 1),
                    rate=specific_rate,
                    rate_type="specific",
                    amount=amount,
                    note=f"{excise_rate_obj.product_name_uz or excise_rate_obj.product_name_ru}: {note}"
                )
            
            # Foizli stavka
            if excise_rate_obj.import_rate_percent:
                percent = excise_rate_obj.import_rate_percent
                amount = excise_base * (percent / 100)
                
                return PaymentItem(
                    name="Excise Tax",
                    name_uz="Aksiz solig'i",
                    base=excise_base,
                    rate=percent,
                    rate_type="percent",
                    amount=amount,
                    note=f"{excise_rate_obj.product_name_uz or excise_rate_obj.product_name_ru}: {percent}%"
                )
        
        # 2. Eski sistema - TariffRate jadvalidagi excise_percent
        if tariff_obj and tariff_obj.excise_percent:
            excise_amount = excise_base * (tariff_obj.excise_percent / 100)
            
            return PaymentItem(
                name="Excise Tax",
                name_uz="Aksiz solig'i",
                base=excise_base,
                rate=tariff_obj.excise_percent,
                rate_type="percent",
                amount=excise_amount
            )
        
        # Aksiz yo'q
        return PaymentItem(
            name="Excise Tax",
            name_uz="Aksiz solig'i",
            base=excise_base,
            rate=0,
            rate_type="percent",
            amount=0,
            note="Aksizga tortilmaydi"
        )
    
    async def _calculate_vat(
        self,
        customs_value_uzs: float,
        import_duty_amount: float,
        excise_amount: float,
        tariff_obj
    ) -> PaymentItem:
        """QQS (VAT) hisoblash"""
        
        vat_base = customs_value_uzs + import_duty_amount + excise_amount
        vat_percent = tariff_obj.vat_percent if tariff_obj else 12.0
        
        vat_amount = vat_base * (vat_percent / 100)
        
        return PaymentItem(
            name="VAT (QQS)",
            name_uz="Qo'shilgan qiymat solig'i (QQS)",
            base=vat_base,
            rate=vat_percent,
            rate_type="percent",
            amount=vat_amount
        )
    
    async def _calculate_utilization_fee(
        self,
        tnved_code: str,
        engine_volume_cc: Optional[int],
        vehicle_age_years: Optional[int]
    ) -> Optional[PaymentItem]:
        """Utilizatsiya yig'imini hisoblash"""
        
        # Faqat avtomobillar uchun (8703 bilan boshlanadigan kodlar)
        if not tnved_code.startswith("8703"):
            return None
        
        util_fee_obj = await utilization_fee.get_by_tnved_code(
            self.db,
            tnved_code=tnved_code,
            engine_volume=engine_volume_cc,
            vehicle_age=vehicle_age_years
        )
        
        if not util_fee_obj:
            self.warnings.append("Avtomobil uchun utilizatsiya yig'imi topilmadi")
            return None
        
        # BRV asosida hisoblash
        if util_fee_obj.fee_type == "brv_multiplier" and util_fee_obj.brv_multiplier:
            brv_obj = await brv_rate.get_current(self.db)
            
            if not brv_obj:
                self.warnings.append("Joriy BRV qiymati topilmadi, default ishlatilmoqda")
                brv_amount = 375000  # 2025 yil default
            else:
                brv_amount = brv_obj.amount
            
            amount = brv_amount * util_fee_obj.brv_multiplier
            
            return PaymentItem(
                name="Utilization Fee",
                name_uz="Utilizatsiya yig'imi",
                base=brv_amount,
                rate=util_fee_obj.brv_multiplier,
                rate_type="brv",
                amount=amount,
                note=f"BRV x {util_fee_obj.brv_multiplier}"
            )
        
        # Foizli
        if util_fee_obj.fee_type == "percent" and util_fee_obj.fee_percent:
            # Bu holda base nima bo'lishi kerak? Bojxona qiymati?
            # Hozircha skip
            pass
        
        # Belgilangan summa
        if util_fee_obj.fee_type == "fixed" and util_fee_obj.fee_amount:
            return PaymentItem(
                name="Utilization Fee",
                name_uz="Utilizatsiya yig'imi",
                base=0,
                rate=util_fee_obj.fee_amount,
                rate_type="fixed",
                amount=util_fee_obj.fee_amount
            )
        
        return None
