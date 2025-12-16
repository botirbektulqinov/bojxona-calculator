from fastapi import APIRouter
from app.api.v1 import tnved, currency, health, calculator, country

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(tnved.router, prefix="/tnved", tags=["tnved"])
api_router.include_router(currency.router, prefix="/currency", tags=["currency"])
api_router.include_router(country.router, prefix="/countries", tags=["countries"])
api_router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
