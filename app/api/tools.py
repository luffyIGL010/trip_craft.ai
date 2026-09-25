from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db import crud
from app.tools import (
    get_weather,
    compare_transport,
    search_hotels,
    get_place_info,
    generate_itinerary,
    book_and_pay,
)

router = APIRouter()


# --- Request models ---

class WeatherRequest(BaseModel):
    city: str
    date: Optional[str] = None


class TransportRequest(BaseModel):
    origin: str
    destination: str
    date: str
    travelers: int = 1
    return_date: Optional[str] = None
    mode_filter: Optional[str] = None


class HotelRequest(BaseModel):
    city: str
    checkin_date: str
    checkout_date: str
    guests: int = 1
    rooms: int = 1
    budget_preference: str = "mid"


class PlaceRequest(BaseModel):
    place_name: str
    city: Optional[str] = None


class ItineraryRequest(BaseModel):
    destination: str
    days: int
    budget_preference: str = "mid"
    interests: Optional[List[str]] = None


class BookingRequest(BaseModel):
    trip_summary: Dict[str, Any]
    traveler_details: List[Dict[str, str]]
    payment_method: str = "UPI / Razorpay"
    user_confirmed: bool = False


# --- Tool endpoints ---

@router.post("/api/tools/get_weather")
async def tool_weather(req: WeatherRequest, user: Any = Depends(get_current_user)):
    return await get_weather(city=req.city, date=req.date)


@router.post("/api/tools/compare_transport")
async def tool_transport(req: TransportRequest, user: Any = Depends(get_current_user)):
    return await compare_transport(
        origin=req.origin,
        destination=req.destination,
        date=req.date,
        travelers=req.travelers,
        return_date=req.return_date,
        mode_filter=req.mode_filter,
    )


@router.post("/api/tools/search_hotels")
async def tool_hotels(req: HotelRequest, user: Any = Depends(get_current_user)):
    return await search_hotels(
        city=req.city,
        checkin_date=req.checkin_date,
        checkout_date=req.checkout_date,
        guests=req.guests,
        rooms=req.rooms,
        budget_preference=req.budget_preference,
    )


@router.post("/api/tools/get_place_info")
async def tool_place(req: PlaceRequest, user: Any = Depends(get_current_user)):
    return await get_place_info(place_name=req.place_name, city=req.city)


@router.post("/api/tools/generate_itinerary")
async def tool_itinerary(req: ItineraryRequest, user: Any = Depends(get_current_user)):
    return await generate_itinerary(
        destination=req.destination,
        days=req.days,
        budget_preference=req.budget_preference,
        interests=req.interests,
    )


@router.post("/api/tools/book_and_pay")
async def tool_booking(
    req: BookingRequest,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    res = await book_and_pay(
        trip_summary=req.trip_summary,
        traveler_details=req.traveler_details,
        payment_method=req.payment_method,
        user_confirmed=req.user_confirmed,
    )
    if res.get("status") == "success":
        await crud.create_booking_record(db, res)
    return res
