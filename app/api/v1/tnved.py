from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.tnved import tnved
from app.schemas.tnved import TNVed

router = APIRouter()

@router.get("/search", response_model=List[TNVed])
async def search_tnved(
    q: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 20
) -> Any:
    """
    Search TNVED codes by code or description.
    """
    results = await tnved.search(db, q=q, limit=limit)
    return results
