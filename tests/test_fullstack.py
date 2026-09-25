import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app.db.database import init_db, AsyncSessionLocal
from app.db import crud
from app.agent.travel_genie import TravelGenieAgent

async def run_fullstack_tests():
    print("\n--- Running TravelGenie Full-Stack Persistence Test Suite ---")
    
    # 1. Initialize Database
    print("\n[1/4] Initializing SQLite database...")
    await init_db()
    print("✅ Database tables created successfully.")

    # 2. Test Session & Chat Message Persistence
    print("\n[2/4] Testing Session and Message Persistence...")
    async with AsyncSessionLocal() as db:
        session = await crud.create_session(db, title="Test Delhi-Goa Trip", session_id="test_sess_001")
        assert session.id == "test_sess_001"
        
        msg1 = await crud.add_message(db, "test_sess_001", "user", "Plan a 3-day trip to Goa")
        msg2 = await crud.add_message(db, "test_sess_001", "assistant", "Here is your plan for Goa!")
        
        history = await crud.get_session_messages(db, "test_sess_001")
        assert len(history) >= 2
        print(f"✅ Session and messages persisted: {len(history)} messages loaded from SQLite.")

    # 3. Test Agent Interaction with DB
    print("\n[3/4] Testing TravelGenie Agent with DB injection...")
    agent = TravelGenieAgent()
    async with AsyncSessionLocal() as db:
        res = await agent.chat("Plan a 3-day trip from Delhi to Goa on a cheap budget", session_id="test_sess_001", db=db)
        assert "Trip Plan: Delhi" in res["reply"]
        
        # Verify trip plan was saved
        trips = await crud.list_trip_plans(db)
        assert len(trips) > 0
        print(f"✅ Trip plan automatically persisted to SQLite: {trips[0].origin} ➔ {trips[0].destination} (Total: ₹{trips[0].total_cost_inr})")

    # 4. Test Booking Persistence
    print("\n[4/4] Testing Booking creation & retrieval...")
    async with AsyncSessionLocal() as db:
        booking_mock = {
            "booking_id": "TG-IN-TEST1234",
            "trip_id": trips[0].id if trips else "mock_trip",
            "travelers": [{"name": "Priya Verma", "contact": "+91-9876543210", "email": "priya@example.com"}],
            "reservations": {
                "transport": {"mode": "FLIGHT", "provider": "IndiGo", "pnr": "AI6E-TEST", "details": "Confirmed"},
                "hotel": {"property_name": "Taj Exotica", "confirmation_code": "HTL-TEST", "checkin": "2026-10-15", "checkout": "2026-10-18"}
            },
            "payment": {"amount_paid_inr": 18500, "status": "PAID_SUCCESSFULLY", "mode": "UPI Instant Pay", "transaction_reference": "TXN_TEST999"}
        }
        b_rec = await crud.create_booking_record(db, booking_mock)
        assert b_rec.id == "TG-IN-TEST1234"
        
        fetched = await crud.get_booking(db, "TG-IN-TEST1234")
        assert fetched is not None
        assert fetched.lead_name == "Priya Verma"
        print(f"✅ Booking record verified: {fetched.id} | Lead: {fetched.lead_name} | Amount: ₹{fetched.total_amount_inr}")

    print("\n🎉 ALL FULL-STACK TESTS PASSED! SQLite Database verified. 🎉\n")

if __name__ == "__main__":
    asyncio.run(run_fullstack_tests())
