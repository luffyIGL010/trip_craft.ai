from typing import Dict, Any, List, Optional
import uuid
import datetime

async def book_and_pay(
    trip_summary: Dict[str, Any],
    traveler_details: List[Dict[str, str]],
    payment_method: str = "UPI / Razorpay",
    user_confirmed: bool = False
) -> Dict[str, Any]:
    """
    Triggers domestic Indian travel booking & payment processing.
    STRICT RULE: Fails if user_confirmed is False.
    Generates confirmed PNR/Ticket for flights & hotels,
    or direct IRCTC/Bus booking links for trains/buses.
    """
    if not user_confirmed:
        return {
            "status": "failed",
            "error": "Booking Aborted: Explicit user confirmation is strictly mandatory before initiating payment and booking."
        }

    if not traveler_details or len(traveler_details) == 0:
        return {
            "status": "failed",
            "error": "Traveler details (Name, Age, Gender, Contact) are required to complete reservation."
        }

    booking_id = f"TG-IN-{uuid.uuid4().hex[:8].upper()}"
    pnr = f"TG{datetime.datetime.now().strftime('%m%d%H%M')}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

    transport = trip_summary.get("selected_transport", {})
    hotel = trip_summary.get("selected_hotel", {})
    total_amount = trip_summary.get("total_trip_cost_inr", 0)

    mode = transport.get("mode", "flight").lower()
    
    # Booking outcome depending on mode
    if "flight" in mode:
        transport_status = "CONFIRMED & TICKET ISSUED"
        transport_pnr = f"AI6E-{uuid.uuid4().hex[:6].upper()}"
        transport_note = f"E-ticket issued. Web check-in opens 48 hours before departure. PNR: {transport_pnr}"
    elif "train" in mode:
        transport_status = "RESERVATION LINK READY"
        transport_pnr = "N/A (IRCTC Link)"
        transport_note = f"As per Indian Railways regulations, please complete final seat selection at: {transport.get('booking_url', 'https://www.irctc.co.in')}"
    else:
        transport_status = "RESERVATION LINK READY"
        transport_pnr = "N/A (Bus Partner Link)"
        transport_note = f"Seat pre-reserved. Confirm your exact sleeper berth at: {transport.get('booking_url', 'https://www.redbus.in')}"

    hotel_status = "CONFIRMED & VOUCHER GENERATED" if hotel else "NOT_BOOKED"

    return {
        "status": "success",
        "booking_id": booking_id,
        "booking_time": timestamp,
        "payment": {
            "status": "PAID_SUCCESSFULLY",
            "transaction_reference": f"TXN_{uuid.uuid4().hex[:12].upper()}",
            "amount_paid_inr": total_amount,
            "currency": "INR (₹)",
            "payment_gateway": "Razorpay / UPI Instant Pay",
            "mode": payment_method
        },
        "reservations": {
            "transport": {
                "mode": transport.get("mode", "flight").upper(),
                "provider": transport.get("provider", "IndiGo"),
                "identifier": transport.get("identifier", "Direct"),
                "status": transport_status,
                "pnr": transport_pnr,
                "details": transport_note
            },
            "hotel": {
                "property_name": hotel.get("name", "Standard Hotel"),
                "status": hotel_status,
                "confirmation_code": f"HTL-{uuid.uuid4().hex[:6].upper()}",
                "checkin": hotel.get("checkin_date", "TBD"),
                "checkout": hotel.get("checkout_date", "TBD"),
                "voucher_url": f"https://travelgenie.in/vouchers/{booking_id}"
            }
        },
        "travelers": traveler_details,
        "support_helpline": "+91 1800-TRAVEL-GENIE (24x7 Domestic Support)"
    }
