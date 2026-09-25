from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.agent.travel_genie import TravelGenieAgent
from app.db.database import init_db, get_db
from app.db import crud
from app.tools import (
    get_weather,
    compare_transport,
    search_hotels,
    get_place_info,
    generate_itinerary,
    book_and_pay
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-stack AI travel planning and booking assistant for Indian domestic travel.",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

agent = TravelGenieAgent()

# Pydantic Request Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

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

# Web UI Route
@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"app_name": settings.APP_NAME})

# Health Check
@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "openweather_configured": bool(settings.OPENWEATHER_API_KEY),
        "database": "SQLite (travelgenie.db)"
    }

# Main Chat Endpoint (with DB Session persistence)
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    response = await agent.chat(user_message=req.message, session_id=req.session_id, db=db)
    return response

# Sessions API
@app.get("/api/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    sessions = await crud.list_sessions(db)
    return [{"id": s.id, "title": s.title, "updated_at": s.updated_at.isoformat() if s.updated_at else None} for s in sessions]

@app.get("/api/sessions/{session_id}/messages")
async def get_session_history(session_id: str, db: AsyncSession = Depends(get_db)):
    msgs = await crud.get_session_messages(db, session_id)
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]

@app.delete("/api/sessions/{session_id}")
async def remove_session(session_id: str, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_session(db, session_id)
    return {"success": ok}

# Trip Plans API
@app.get("/api/trips")
async def get_saved_trips(db: AsyncSession = Depends(get_db)):
    trips = await crud.list_trip_plans(db)
    return trips

# Bookings API
@app.get("/api/bookings")
async def get_bookings(db: AsyncSession = Depends(get_db)):
    bookings = await crud.list_bookings(db)
    return bookings

@app.get("/api/bookings/{booking_id}")
async def get_booking_details(booking_id: str, db: AsyncSession = Depends(get_db)):
    b = await crud.get_booking(db, booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return b

# Tool Endpoints
@app.post("/api/tools/get_weather")
async def tool_weather(req: WeatherRequest):
    return await get_weather(city=req.city, date=req.date)

@app.post("/api/tools/compare_transport")
async def tool_transport(req: TransportRequest):
    return await compare_transport(
        origin=req.origin,
        destination=req.destination,
        date=req.date,
        travelers=req.travelers,
        return_date=req.return_date,
        mode_filter=req.mode_filter
    )

@app.post("/api/tools/search_hotels")
async def tool_hotels(req: HotelRequest):
    return await search_hotels(
        city=req.city,
        checkin_date=req.checkin_date,
        checkout_date=req.checkout_date,
        guests=req.guests,
        rooms=req.rooms,
        budget_preference=req.budget_preference
    )

@app.post("/api/tools/get_place_info")
async def tool_place(req: PlaceRequest):
    return await get_place_info(place_name=req.place_name, city=req.city)

@app.post("/api/tools/generate_itinerary")
async def tool_itinerary(req: ItineraryRequest):
    return await generate_itinerary(
        destination=req.destination,
        days=req.days,
        budget_preference=req.budget_preference,
        interests=req.interests
    )

@app.post("/api/tools/book_and_pay")
async def tool_booking(req: BookingRequest, db: AsyncSession = Depends(get_db)):
    res = await book_and_pay(
        trip_summary=req.trip_summary,
        traveler_details=req.traveler_details,
        payment_method=req.payment_method,
        user_confirmed=req.user_confirmed
    )
    if res.get("status") == "success":
        await crud.create_booking_record(db, res)
    return res
