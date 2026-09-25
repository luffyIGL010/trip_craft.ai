from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.db import crud

router = APIRouter()


@router.get("/api/trips")
async def get_saved_trips(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    return await crud.list_trip_plans(db)
