import json
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ChatSessionModel, ChatMessageModel, TripPlanModel, BookingModel

# --- Sessions ---
async def create_session(db: AsyncSession, title: str = "New Domestic Trip", session_id: Optional[str] = None) -> ChatSessionModel:
    sid = session_id or str(uuid.uuid4())
    session = ChatSessionModel(id=sid, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_or_create_session(db: AsyncSession, session_id: str, title: Optional[str] = None) -> ChatSessionModel:
    result = await db.execute(select(ChatSessionModel).where(ChatSessionModel.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        session = ChatSessionModel(id=session_id, title=title or "Domestic Trip Plan")
        db.add(session)
        await db.commit()
        await db.refresh(session)
    return session

async def list_sessions(db: AsyncSession) -> List[ChatSessionModel]:
    result = await db.execute(select(ChatSessionModel).order_by(desc(ChatSessionModel.updated_at)))
    return list(result.scalars().all())

async def delete_session(db: AsyncSession, session_id: str) -> bool:
    result = await db.execute(delete(ChatSessionModel).where(ChatSessionModel.id == session_id))
    await db.commit()
    return result.rowcount > 0

# --- Messages ---
async def add_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    tool_calls: Optional[List[Any]] = None,
    quote: Optional[Dict[str, Any]] = None
) -> ChatMessageModel:
    # Ensure session exists
    await get_or_create_session(db, session_id)
    
    msg = ChatMessageModel(
        session_id=session_id,
        role=role,
        content=content,
        tool_calls_json=json.dumps(tool_calls) if tool_calls else None,
        quote_json=json.dumps(quote) if quote else None
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_session_messages(db: AsyncSession, session_id: str) -> List[ChatMessageModel]:
    result = await db.execute(
        select(ChatMessageModel)
        .where(ChatMessageModel.session_id == session_id)
        .order_by(ChatMessageModel.id)
    )
    return list(result.scalars().all())

# --- Trip Plans ---
async def save_trip_plan(db: AsyncSession, trip_data: Dict[str, Any]) -> TripPlanModel:
    trip = TripPlanModel(
        id=trip_data.get("id") or str(uuid.uuid4()),
        session_id=trip_data.get("session_id"),
        origin=trip_data.get("origin", "Delhi"),
        destination=trip_data.get("destination", "Goa"),
        start_date=trip_data.get("start_date", "2026-10-15"),
        end_date=trip_data.get("end_date", "2026-10-18"),
        duration_days=trip_data.get("duration_days", 3),
        travelers=trip_data.get("travelers", 1),
        budget_preference=trip_data.get("budget_preference", "mid"),
        total_cost_inr=float(trip_data.get("total_cost_inr", 0)),
        summary_json=json.dumps(trip_data.get("summary", {}))
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip

async def list_trip_plans(db: AsyncSession) -> List[TripPlanModel]:
    result = await db.execute(select(TripPlanModel).order_by(desc(TripPlanModel.created_at)))
    return list(result.scalars().all())

async def get_trip_plan(db: AsyncSession, trip_id: str) -> Optional[TripPlanModel]:
    result = await db.execute(select(TripPlanModel).where(TripPlanModel.id == trip_id))
    return result.scalar_one_or_none()

# --- Bookings ---
async def create_booking_record(db: AsyncSession, b: Dict[str, Any]) -> BookingModel:
    lead = b.get("travelers", [{}])[0]
    resv = b.get("reservations", {})
    t = resv.get("transport", {})
    h = resv.get("hotel", {})
    p = b.get("payment", {})

    record = BookingModel(
        id=b.get("booking_id"),
        trip_id=b.get("trip_id"),
        lead_name=lead.get("name", "Primary Traveler"),
        lead_phone=lead.get("contact", "+91-9876543210"),
        lead_email=lead.get("email", "traveler@example.com"),
        transport_mode=t.get("mode", "FLIGHT"),
        transport_provider=t.get("provider", "IndiGo"),
        transport_pnr=t.get("pnr", "N/A"),
        transport_details=t.get("details", ""),
        hotel_name=h.get("property_name", "Standard Hotel"),
        hotel_confirmation=h.get("confirmation_code", "CONFIRMED"),
        hotel_dates=f"{h.get('checkin', '')} to {h.get('checkout', '')}",
        total_amount_inr=float(p.get("amount_paid_inr", 0)),
        payment_status=p.get("status", "PAID_SUCCESSFULLY"),
        payment_method=p.get("mode", "UPI Instant Pay"),
        transaction_reference=p.get("transaction_reference", "TXN_MOCK"),
        travelers_json=json.dumps(b.get("travelers", []))
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

async def list_bookings(db: AsyncSession) -> List[BookingModel]:
    result = await db.execute(select(BookingModel).order_by(desc(BookingModel.created_at)))
    return list(result.scalars().all())

async def get_booking(db: AsyncSession, booking_id: str) -> Optional[BookingModel]:
    result = await db.execute(select(BookingModel).where(BookingModel.id == booking_id))
    return result.scalar_one_or_none()
