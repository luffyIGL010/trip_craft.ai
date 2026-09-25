from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auth_provider = Column(String(32), nullable=False) # "google", "phone"
    provider_user_id = Column(String(128), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False, default="Traveler")
    email = Column(String(128), nullable=True, index=True)
    phone_number = Column(String(32), nullable=True, index=True)
    profile_image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship("ChatSessionModel", back_populates="user", cascade="all, delete-orphan")
    trips = relationship("TripPlanModel", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("BookingModel", back_populates="user", cascade="all, delete-orphan")

class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), default="New Domestic Trip")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="sessions")
    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessageModel.id")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls_json = Column(Text, nullable=True)
    quote_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSessionModel", back_populates="messages")

class TripPlanModel(Base):
    __tablename__ = "trip_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    origin = Column(String(128), nullable=False)
    destination = Column(String(128), nullable=False)
    start_date = Column(String(32), nullable=False)
    end_date = Column(String(32), nullable=False)
    duration_days = Column(Integer, default=3)
    travelers = Column(Integer, default=1)
    budget_preference = Column(String(32), default="mid")
    total_cost_inr = Column(Float, nullable=False)
    summary_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="trips")

class BookingModel(Base):
    __tablename__ = "bookings"

    id = Column(String(64), primary_key=True)  # TG-IN-XXXX
    trip_id = Column(String(36), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_name = Column(String(128), nullable=False)
    lead_phone = Column(String(32), nullable=False)
    lead_email = Column(String(128), default="traveler@example.com")
    transport_mode = Column(String(32), default="FLIGHT")
    transport_provider = Column(String(64), default="IndiGo")
    transport_pnr = Column(String(64), default="N/A")
    transport_details = Column(Text, nullable=True)
    hotel_name = Column(String(128), default="Verified Hotel")
    hotel_confirmation = Column(String(64), default="CONFIRMED")
    hotel_dates = Column(String(64), default="")
    total_amount_inr = Column(Float, nullable=False)
    payment_status = Column(String(32), default="PAID_SUCCESSFULLY")
    payment_method = Column(String(64), default="UPI Instant Pay")
    transaction_reference = Column(String(64), nullable=False)
    travelers_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="bookings")
