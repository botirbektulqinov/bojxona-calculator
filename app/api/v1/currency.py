from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.currency import currency
from app.schemas.currency import Currency
from app.parsers.currency_updater import currency_updater

router = APIRouter()


@router.get("/", response_model=List[Currency])
async def get_currencies(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Barcha valyutalar ro'yxatini olish (eng oxirgi kurslar).
    """
    rates = await currency.get_latest_rates(db)
    return rates


@router.get("/rates", response_model=List[Currency])
async def get_current_rates(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Joriy valyuta kurslarini olish.
    """
    rates = await currency.get_latest_rates(db)
    return rates


@router.get("/rate/{code}")
async def get_rate(
    code: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Bitta valyuta kursini olish.
    
    Args:
        code: Valyuta kodi (USD, EUR, RUB...)
    """
    rate = await currency.get_latest_rate(db, code=code.upper())
    if not rate:
        raise HTTPException(status_code=404, detail=f"Valyuta topilmadi: {code}")
    
    return {
        "code": rate.code,
        "name": rate.name,
        "rate": float(rate.rate_uzs),
        "nominal": rate.nominal,
        "rate_per_unit": float(rate.rate_uzs) / rate.nominal if rate.nominal else float(rate.rate_uzs),
        "diff": float(rate.diff) if rate.diff else 0,
        "date": rate.date.isoformat()
    }


@router.post("/update")
async def update_rates(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    CBU API dan valyuta kurslarini yangilash.
    
    Bu endpoint Markaziy Bank API dan joriy kurslarni oladi va bazaga saqlaydi.
    """
    result = await currency_updater.update_rates(db)
    return {
        "status": "success" if not result["errors"] else "partial",
        "updated": result["updated"],
        "errors": result["errors"],
        "message": f"{result['updated']} ta valyuta yangilandi"
    }
