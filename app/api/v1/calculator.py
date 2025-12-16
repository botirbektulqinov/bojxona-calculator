from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.calculator import CustomsCalculator, CalculationInput

router = APIRouter()


class CalculateRequest(BaseModel):
    code: str = Field(..., description="TN VED kodi (10 raqam)", min_length=2, max_length=10)
    price: float = Field(..., description="Tovar narxi (invoys)", gt=0)
    currency: str = Field(default="USD", description="Valyuta kodi")
    weight: float = Field(..., description="Vazn (kg)", ge=0)
    quantity: Optional[int] = Field(default=None, description="Miqdor (dona)")
    country_origin: str = Field(default="XX", description="Kelib chiqish mamlakatsi (ISO kod)")
    has_certificate: bool = Field(default=False, description="ST-1 sertifikati bormi")
    delivery_cost: float = Field(default=0, description="Yetkazib berish narxi", ge=0)
    insurance_cost: float = Field(default=0, description="Sug'urta narxi", ge=0)
    engine_volume: Optional[int] = Field(default=None, description="Dvigatel hajmi (sm³)")
    vehicle_age: Optional[int] = Field(default=None, description="Avtomobil yoshi (yil)")


class PaymentItemResponse(BaseModel):
    name: str
    name_uz: str
    base: float
    rate: Optional[float]
    rate_type: str
    amount: float
    note: Optional[str] = None


class CalculationResponse(BaseModel):
    customs_value_uzs: float
    customs_value_usd: float
    payments: List[PaymentItemResponse]
    total_uzs: float
    total_usd: float
    effective_rate_percent: float
    exchange_rate: float
    duty_rate_type: str
    details: dict
    warnings: List[str]
    data_source: str = "incustoms.ai"  # Ma'lumotlar manbai
    sync_info: Optional[str] = "TN VED kodlar va tariflar incustoms.ai dan sinxronlangan"


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_customs(
    payload: CalculateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Bojxona to'lovlarini hisoblash.
    
    - **code**: TN VED kodi (2-10 raqam)
    - **price**: Tovar narxi (invoys)
    - **currency**: Valyuta kodi (USD, EUR, UZS, RUB, CNY)
    - **weight**: Vazn (kg)
    - **country_origin**: Kelib chiqish mamlakatsi (ISO kod, masalan: CN, RU, DE)
    - **has_certificate**: ST-1 kelib chiqish sertifikati bormi
    - **delivery_cost**: Yetkazib berish xarajati
    - **insurance_cost**: Sug'urta xarajati
    - **engine_volume**: Avtomobil dvigatel hajmi (sm³) - avtomobillar uchun
    - **vehicle_age**: Avtomobil yoshi (yil) - avtomobillar uchun
    """
    try:
        calc_input = CalculationInput(
            tnved_code=payload.code,
            price=payload.price,
            currency_code=payload.currency,
            weight_kg=payload.weight,
            quantity=payload.quantity,
            country_origin=payload.country_origin,
            has_origin_certificate=payload.has_certificate,
            delivery_cost=payload.delivery_cost,
            insurance_cost=payload.insurance_cost,
            engine_volume_cc=payload.engine_volume,
            vehicle_age_years=payload.vehicle_age
        )        
        calculator = CustomsCalculator(db)
        result = await calculator.calculate(calc_input)
        
        return CalculationResponse(
            customs_value_uzs=round(result.customs_value_uzs, 2),
            customs_value_usd=round(result.customs_value_usd, 2),
            payments=[
                PaymentItemResponse(
                    name=p.name,
                    name_uz=p.name_uz,
                    base=round(p.base, 2),
                    rate=p.rate,
                    rate_type=p.rate_type,
                    amount=round(p.amount, 2),
                    note=p.note
                )
                for p in result.payments
            ],
            total_uzs=round(result.total_uzs, 2),
            total_usd=round(result.total_usd, 2),
            effective_rate_percent=result.effective_rate_percent,
            exchange_rate=result.exchange_rate,
            duty_rate_type=result.duty_rate_type.value,
            details=result.details,
            warnings=result.warnings,
            data_source="incustoms.ai",
            sync_info="TN VED kodlar va tariflar incustoms.ai dan sinxronlangan (14,033 kod)"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hisoblash xatosi: {str(e)}")


class SimpleCalculateRequest(BaseModel):
    code: str
    price: float
    currency: str = "USD"
    weight: float
    country_origin: str = "CN"


class SimpleCalculationResult(BaseModel):
    customs_value_uzs: float
    customs_fee: float
    duty: float
    excise: float
    vat: float
    total: float
    details: dict


@router.post("/calculate/simple", response_model=SimpleCalculationResult)
async def calculate_customs_simple(
    payload: SimpleCalculateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        cis_countries = ["RU", "KZ", "KG", "TJ", "BY", "AM", "AZ", "MD", "UA", "GE"]
        has_cert = payload.country_origin in cis_countries
        
        calc_input = CalculationInput(
            tnved_code=payload.code,
            price=payload.price,
            currency_code=payload.currency,
            weight_kg=payload.weight,
            country_origin=payload.country_origin,
            has_origin_certificate=has_cert
        )
        
        calculator = CustomsCalculator(db)
        result = await calculator.calculate(calc_input)
        payments_dict = {p.name: p.amount for p in result.payments}
        
        return SimpleCalculationResult(
            customs_value_uzs=round(result.customs_value_uzs, 2),
            customs_fee=round(payments_dict.get("Customs Fee", 0), 2),
            duty=round(payments_dict.get("Import Duty", 0), 2),
            excise=round(payments_dict.get("Excise Tax", 0), 2),
            vat=round(payments_dict.get("VAT (QQS)", 0), 2),
            total=round(result.total_uzs, 2),
            details={
                "exchange_rate": result.exchange_rate,
                "tariff_duty_percent": result.details.get("tariff_duty_percent"),
                "tariff_excise_percent": result.details.get("tariff_excise_percent"),
                "duty_rate_type": result.duty_rate_type.value,
                "warnings": result.warnings
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hisoblash xatosi: {str(e)}")
