from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from datetime import datetime, time

from app.core.config import settings
from app.api.v1.init import api_router
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.models.init import TNVedCode, TariffRate, Currency, Country, FreeTradeCountry, UtilizationFee, TariffBenefit, CustomsFeeRate, BRVRate
from app.parsers.currency_updater import CurrencyUpdater
_background_task = None


async def update_currency_rates():
    try:
        updater = CurrencyUpdater()
        async with AsyncSessionLocal() as db:
            await updater.update_rates(db)
    except Exception as e:
        pass  


async def daily_currency_update():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if now.time() >= time(9, 0):
            from datetime import timedelta
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        await update_currency_rates()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _background_task
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)    
    await update_currency_rates()
    _background_task = asyncio.create_task(daily_currency_update())
    
    yield    
    if _background_task:
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, 'index.html'))
