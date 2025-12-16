from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.country import country, free_trade_country
from app.schemas.country import Country, FreeTradeCountry

router = APIRouter()


@router.get("/", response_model=List[Country])
async def get_countries(
    db: AsyncSession = Depends(get_db)
) -> Any:
    countries = await country.get_all_active(db)
    return countries


@router.get("/list", response_model=List[Country])
async def get_countries_list(
    db: AsyncSession = Depends(get_db)
) -> Any:
    countries = await country.get_all_active(db)
    return countries


@router.get("/search", response_model=List[Country])
async def search_countries(
    q: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 20
) -> Any:
    results = await country.search(db, q=q, limit=limit)
    return results


@router.get("/free-trade", response_model=List[FreeTradeCountry])
async def get_free_trade_countries(
    db: AsyncSession = Depends(get_db)
) -> Any:
    countries = await free_trade_country.get_all(db)
    return countries


@router.get("/check-free-trade/{country_code}")
async def check_free_trade(
    country_code: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    is_free = await free_trade_country.is_free_trade(db, country_code=country_code)
    ftc = await free_trade_country.get_by_code(db, country_code=country_code)
    
    return {
        "country_code": country_code.upper(),
        "is_free_trade": is_free,
        "agreement_name": ftc.agreement_name if ftc else None,
        "requires_certificate": ftc.requires_certificate if ftc else None
    }
