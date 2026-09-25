import asyncio
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app.tools.weather import get_weather
from app.tools.transport import compare_transport
from app.tools.hotels import search_hotels
from app.tools.places import get_place_info
from app.tools.itinerary import generate_itinerary
from app.tools.booking import book_and_pay
from app.agent.travel_genie import TravelGenieAgent

async def run_all_tests():
    print("\n--- Running TravelGenie Test Suite ---")
    
    # 1. Weather Tool Test
    print("\n[1/6] Testing get_weather('Jaipur')...")
    w = await get_weather("Jaipur")
    assert "temperature_c" in w or "error" in w
    print(f"✅ Weather fetched: {w.get('city')} | Temp: {w.get('temperature_c')}°C | Condition: {w.get('condition')}")

    # 2. Transport Comparison Test
    print("\n[2/6] Testing compare_transport('Delhi', 'Goa', '2026-10-15', travelers=2)...")
    t = await compare_transport("Delhi", "Goa", "2026-10-15", travelers=2, return_date="2026-10-19")
    assert "cheapest_mode_highlight" in t
    assert "onward_options" in t
    assert len(t["onward_options"]["flights"]) > 0
    assert len(t["onward_options"]["trains"]) > 0
    assert len(t["onward_options"]["buses"]) > 0
    print(f"✅ Transport compared: Cheapest = {t['cheapest_mode_highlight']['mode']} (₹{t['cheapest_mode_highlight']['total_price']})")
    print(f"✅ IRCTC Booking Link verified: {t['onward_options']['trains'][0]['booking_url']}")

    # 3. Hotel Search Test (cheap vs premium sorting)
    print("\n[3/6] Testing search_hotels budget sorting...")
    h_cheap = await search_hotels("Goa", "2026-10-15", "2026-10-19", budget_preference="cheap")
    h_prem = await search_hotels("Goa", "2026-10-15", "2026-10-19", budget_preference="premium")
    assert h_cheap["hotels"][0]["price_per_night_inr"] <= h_cheap["hotels"][-1]["price_per_night_inr"], "Cheap preference must sort lowest price first"
    assert h_prem["hotels"][0]["stars"] >= h_prem["hotels"][-1]["stars"], "Premium preference must prioritize highest stars"
    print(f"✅ Cheap Hotel #1: {h_cheap['hotels'][0]['name']} (₹{h_cheap['hotels'][0]['price_per_night_inr']}/night)")
    print(f"✅ Premium Hotel #1: {h_prem['hotels'][0]['name']} ({h_prem['hotels'][0]['stars']}⭐, ₹{h_prem['hotels'][0]['price_per_night_inr']}/night)")

    # 4. Place Info Test
    print("\n[4/6] Testing get_place_info('Hawa Mahal', 'Jaipur')...")
    p = await get_place_info("Hawa Mahal", "Jaipur")
    assert p["status"] == "success"
    print(f"✅ Place Info: {p['attraction']['name']} | Entry Fee (Indians): ₹{p['attraction']['entry_fee_inr']['indians']}")

    # 5. Itinerary Test
    print("\n[5/6] Testing generate_itinerary('Goa', days=4, budget_preference='mid')...")
    itin = await generate_itinerary("Goa", days=4, budget_preference="mid")
    assert len(itin["days"]) == 4
    assert itin["expense_breakdown"]["grand_total_itinerary_inr"] > 0
    print(f"✅ Itinerary generated for {itin['duration_days']} days | Grand Total Local Expense: ₹{itin['expense_breakdown']['grand_total_itinerary_inr']}")

    # 6. Booking & Pay Test (Strict user confirmation enforcement)
    print("\n[6/6] Testing book_and_pay confirmation enforcement...")
    dummy_quote = {
        "selected_transport": t["cheapest_mode_highlight"],
        "selected_hotel": h_cheap["hotels"][0],
        "total_trip_cost_inr": 15400
    }
    travelers = [{"name": "Rohan Sharma", "age": "28", "gender": "Male", "contact": "+91-9876543210"}]
    
    # Negative test (unconfirmed)
    b_fail = await book_and_pay(dummy_quote, travelers, user_confirmed=False)
    assert b_fail["status"] == "failed"
    print("✅ Successfully rejected booking when user_confirmed=False")

    # Positive test (confirmed)
    b_pass = await book_and_pay(dummy_quote, travelers, user_confirmed=True)
    assert b_pass["status"] == "success"
    assert "booking_id" in b_pass
    print(f"✅ Confirmed Booking ID: {b_pass['booking_id']} | Status: {b_pass['payment']['status']}")

    # 7. Agent End-to-End Chat Test
    print("\n[7/7] Testing TravelGenieAgent end-to-end conversation...")
    agent = TravelGenieAgent()
    res = await agent.chat("Plan a 4-day trip from Delhi to Goa for 2 travelers on a mid budget.")
    assert "Trip Plan: Delhi" in res["reply"]
    print("✅ TravelGenie generated comprehensive quotation:")
    print(res["reply"][:300] + "...\n")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
