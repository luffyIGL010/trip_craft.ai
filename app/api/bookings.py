from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.db import crud
from app.tools import book_and_pay

router = APIRouter()


class BookingRequest(BaseModel):
    trip_summary: Dict[str, AnyType]
    traveler_details: List[Dict[str, str]]
    payment_method: str = "UPI / Razorpay"
    user_confirmed: bool = False


@router.get("/api/bookings")
async def get_bookings(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    return await crud.list_bookings(db)


@router.get("/api/bookings/{booking_id}")
async def get_booking_details(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    b = await crud.get_booking(db, booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return b
