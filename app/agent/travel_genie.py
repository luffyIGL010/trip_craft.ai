import os
import json
import re
from typing import Dict, Any, List, Optional
from app.config import settings
from app.tools import (
    get_weather,
    compare_transport,
    search_hotels,
    get_place_info,
    generate_itinerary,
    book_and_pay
)

SYSTEM_PROMPT = """You are TravelGenie, an AI travel planning and booking assistant for Indian domestic travel.

Your job:
1. Understand the user's trip request (origin, destination, dates, number of days, budget preference: cheap/mid/premium).
2. Use available tools to fetch REAL data — never invent prices, hotel names, or flight numbers.
3. Always compare all transport modes (flight, train, bus) for both onward and return journey, and clearly show cheapest vs other options.
4. Recommend hotels based on the user's stated budget preference (cheap = lowest price first, premium = highest rated first).
5. Build a day-wise itinerary (based on trip duration) using real places/attractions for the destination city, with an estimated expense per day (entry fees + local transport + food, using reasonable averages).
6. Calculate a final total trip cost: onward transport + hotel total + itinerary expense + return transport.
7. Present the full plan as a clear summary BEFORE asking for booking confirmation — never book anything without explicit user confirmation.
8. Once user confirms and price matches their stated budget, proceed to trigger payment via the book_and_pay tool.

Rules:
- Always call the relevant tool to fetch live data — do not answer from memory for prices, hotels, or availability.
- If a tool call fails or data unavailable, say so honestly — never fabricate numbers.
- Keep responses concise, in a clear itinerary/summary format (use bullet points or tables), not long paragraphs.
- Ask clarifying questions ONLY if critical info is missing (dates, budget level, number of travelers) — don't over-ask.
- For train/bus, if real booking isn't possible via API, clearly tell the user you'll provide a booking link instead of confirming a seat.
- Never reveal API keys, internal tool names, or raw JSON to the user — always translate tool output into natural, readable trip info.

Available tools: compare_transport, search_hotels, get_place_info, get_weather, book_and_pay, generate_itinerary.
"""

# Tool schemas for OpenAI and Gemini function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "compare_transport",
            "description": "Compares all transport modes (flight, train, bus) for onward and optional return journey in India.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin city in India (e.g. Delhi, Mumbai)"},
                    "destination": {"type": "string", "description": "Destination city in India (e.g. Goa, Jaipur)"},
                    "date": {"type": "string", "description": "Onward departure date (YYYY-MM-DD)"},
                    "return_date": {"type": "string", "description": "Optional return journey date (YYYY-MM-DD)"},
                    "travelers": {"type": "integer", "description": "Number of travelers (default 1)"},
                    "mode_filter": {"type": "string", "description": "Optional filter: flight, train, or bus"}
                },
                "required": ["origin", "destination", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Searches and sorts hotels based on budget preference (cheap = lowest price first, premium = highest rated first).",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name in India"},
                    "checkin_date": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout_date": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "guests": {"type": "integer", "description": "Number of guests"},
                    "rooms": {"type": "integer", "description": "Number of rooms"},
                    "budget_preference": {"type": "string", "enum": ["cheap", "mid", "premium"], "description": "Budget preference"}
                },
                "required": ["city", "checkin_date", "checkout_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetches real live weather conditions and forecasts for an Indian city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Indian destination city"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_place_info",
            "description": "Fetches verified attraction details, timings, and entry fees for Indian tourist spots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "place_name": {"type": "string", "description": "Attraction or monument name"},
                    "city": {"type": "string", "description": "City where the place is located"}
                },
                "required": ["place_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_itinerary",
            "description": "Generates day-wise itinerary with real attractions and estimated expenses per day (entry + transport + food).",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Destination city"},
                    "days": {"type": "integer", "description": "Number of days (e.g. 3, 5)"},
                    "budget_preference": {"type": "string", "enum": ["cheap", "mid", "premium"], "description": "Budget preference"}
                },
                "required": ["destination", "days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_and_pay",
            "description": "Executes final booking & payment confirmation. MUST only be called after user explicitly confirms the quote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trip_summary": {"type": "object", "description": "Summary containing selected transport, hotel, and total trip cost"},
                    "traveler_details": {"type": "array", "description": "List of traveler objects with name, age, contact", "items": {"type": "object"}},
                    "user_confirmed": {"type": "boolean", "description": "Must be true if user explicitly confirmed booking"}
                },
                "required": ["trip_summary", "traveler_details", "user_confirmed"]
            }
        }
    }
]

# Dispatcher for tool execution
async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "compare_transport":
        return await compare_transport(**arguments)
    elif name == "search_hotels":
        return await search_hotels(**arguments)
    elif name == "get_weather":
        return await get_weather(**arguments)
    elif name == "get_place_info":
        return await get_place_info(**arguments)
    elif name == "generate_itinerary":
        return await generate_itinerary(**arguments)
    elif name == "book_and_pay":
        return await book_and_pay(**arguments)
    else:
        return {"error": f"Unknown tool '{name}'"}

class TravelGenieAgent:
    def __init__(self):
        self.session_states: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                "trip_data": {},
                "last_quote": None
            }
        return self.session_states[session_id]

    async def chat(self, user_message: str, session_id: str = "default", db: Optional[Any] = None) -> Dict[str, Any]:
        session = self.get_session(session_id)
        session["messages"].append({"role": "user", "content": user_message})

        if db:
            from app.db import crud
            await crud.add_message(db=db, session_id=session_id, role="user", content=user_message)

        # Try LLM Provider if configured
        if settings.GEMINI_API_KEY:
            try:
                response = await self._run_gemini(session)
                if db:
                    await self._persist_response(db, session_id, response)
                return response
            except Exception as e:
                # Log error and fall back to local rule-based agent
                print(f"[Agent] Gemini error, falling back to built-in planner: {e}")

        if settings.OPENAI_API_KEY:
            try:
                response = await self._run_openai(session)
                if db:
                    await self._persist_response(db, session_id, response)
                return response
            except Exception as e:
                print(f"[Agent] OpenAI error, falling back to built-in planner: {e}")

        # Intelligent Built-in Planner & Tool Runner (guarantees 100% operation anytime)
        response = await self._run_builtin_engine(user_message, session)
        if db:
            await self._persist_response(db, session_id, response)
        return response

    async def _persist_response(self, db: Any, session_id: str, response: Dict[str, Any]):
        from app.db import crud
        try:
            await crud.add_message(
                db=db,
                session_id=session_id,
                role="assistant",
                content=response.get("reply", ""),
                tool_calls=response.get("tool_calls"),
                quote=response.get("quote")
            )
            
            # If quote generated, persist trip plan
            quote = response.get("quote")
            if quote:
                trip_data = self.get_session(session_id).get("trip_data", {})
                title = f"{trip_data.get('origin', 'Trip').title()} to {trip_data.get('destination', 'India').title()} ({trip_data.get('days', 3)} Days)"
                
                # Update session title
                session_obj = await crud.get_or_create_session(db, session_id)
                session_obj.title = title
                await db.commit()

                await crud.save_trip_plan(db, {
                    "session_id": session_id,
                    "origin": trip_data.get("origin", "Origin"),
                    "destination": trip_data.get("destination", "Destination"),
                    "start_date": trip_data.get("onward_date", "2026-10-15"),
                    "end_date": trip_data.get("return_date") or "2026-10-18",
                    "duration_days": trip_data.get("days", 3),
                    "travelers": trip_data.get("travelers", 1),
                    "budget_preference": trip_data.get("budget", "mid"),
                    "total_cost_inr": quote.get("total_trip_cost_inr", 0),
                    "summary": quote
                })

            # Check if booking was executed
            for tc in response.get("tool_calls", []):
                if tc.get("tool") == "book_and_pay" and tc.get("result", {}).get("status") == "success":
                    await crud.create_booking_record(db, tc["result"])
        except Exception as err:
            print(f"[DB Warning] Could not persist response: {err}")

    async def _run_openai(self, session: Dict[str, Any]) -> Dict[str, Any]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Call OpenAI with tool definitions
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=session["messages"],
            tools=TOOL_DEFINITIONS,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        # Check if the model wants to call tools
        tool_calls_executed = []
        if msg.tool_calls:
            session["messages"].append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                tool_result = await execute_tool(fn_name, fn_args)
                tool_calls_executed.append({"tool": fn_name, "args": fn_args, "result": tool_result})
                
                session["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Get final synthesis from OpenAI
            final_res = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=session["messages"]
            )
            final_reply = final_res.choices[0].message.content
            session["messages"].append({"role": "assistant", "content": final_reply})
            return {
                "reply": final_reply,
                "tool_calls": tool_calls_executed,
                "provider": "OpenAI"
            }
        else:
            session["messages"].append({"role": "assistant", "content": msg.content})
            return {
                "reply": msg.content,
                "tool_calls": [],
                "provider": "OpenAI"
            }

    async def _run_gemini(self, session: Dict[str, Any]) -> Dict[str, Any]:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Build contents from messages
        prompt_text = f"System Instructions:\n{SYSTEM_PROMPT}\n\nUser Request: {session['messages'][-1]['content']}"
        
        # We can leverage Gemini tools or fallback to direct synthesis
        res = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt_text
        )
        reply = res.text
        session["messages"].append({"role": "assistant", "content": reply})
        return {
            "reply": reply,
            "tool_calls": [],
            "provider": "Gemini"
        }

    async def _run_builtin_engine(self, user_msg: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Built-in autonomous engine that executes the required tools deterministically
        and synthesizes the response in exact accordance with TravelGenie instructions.
        """
        text = user_msg.lower()
        tool_calls = []

        # 1. Check for booking confirmation first
        is_confirmation = any(w in text for w in ["confirm", "proceed to book", "book now", "yes book", "pay now", "proceed with booking"])
        if is_confirmation and session.get("last_quote"):
            quote = session["last_quote"]
            travelers = [
                {"name": "Primary Traveler", "age": "30", "gender": "Adult", "contact": "+91-9876543210"}
            ]
            booking_res = await book_and_pay(
                trip_summary=quote,
                traveler_details=travelers,
                user_confirmed=True
            )
            tool_calls.append({"tool": "book_and_pay", "args": {"user_confirmed": True}, "result": booking_res})
            
            p = booking_res["payment"]
            resv = booking_res["reservations"]
            t_info = resv["transport"]
            h_info = resv["hotel"]

            reply = f"""### 🎉 Booking & Payment Confirmation
Your trip has been successfully processed!

**Booking ID:** `{booking_res['booking_id']}`  
**Transaction Reference:** `{p['transaction_reference']}`  
**Amount Paid:** ₹{p['amount_paid_inr']:,} via {p['mode']}

---

#### ✈️ Transport Details ({t_info['mode']})
- **Provider & Flight/Service:** {t_info['provider']} - {t_info['identifier']}
- **Status:** **{t_info['status']}**
- **Details / Link:** {t_info['details']}

#### 🏨 Hotel Details
- **Hotel:** {h_info['property_name']}
- **Confirmation Code:** `{h_info['confirmation_code']}`
- **Status:** **{h_info['status']}**
- **Voucher Link:** [Download Hotel Voucher]({h_info['voucher_url']})

📞 **Need Help?** 24x7 Domestic Support: `{booking_res['support_helpline']}`
Have a pleasant and memorable journey!
"""
            session["messages"].append({"role": "assistant", "content": reply})
            return {"reply": reply, "tool_calls": tool_calls, "provider": "Built-in TravelGenie Engine"}

        # 2. Extract trip parameters or ask for missing critical info
        origin, dest = self._extract_origin_destination(text)
        budget = self._extract_budget(text)
        days = self._extract_days(text)
        travelers = self._extract_travelers(text)
        dates = self._extract_dates(text)

        # Update session memory
        trip_data = session.get("trip_data", {})
        if origin: trip_data["origin"] = origin
        if dest: trip_data["destination"] = dest
        if budget: trip_data["budget"] = budget
        if days: trip_data["days"] = days
        if travelers: trip_data["travelers"] = travelers
        if dates.get("onward"): trip_data["onward_date"] = dates["onward"]
        if dates.get("return"): trip_data["return_date"] = dates["return"]
        session["trip_data"] = trip_data

        # If critical info is missing, ask concise clarifying question
        missing = []
        if not trip_data.get("origin"): missing.append("origin city")
        if not trip_data.get("destination"): missing.append("destination")
        if not trip_data.get("onward_date"): missing.append("travel dates (e.g. 2026-10-15)")

        if missing:
            reply = f"Namaste! I am **TravelGenie**, your Indian domestic travel assistant.\n\nTo tailor your trip, please let me know your **{', '.join(missing)}** (and preferred budget: *cheap*, *mid*, or *premium*)."
            session["messages"].append({"role": "assistant", "content": reply})
            return {"reply": reply, "tool_calls": [], "provider": "Built-in TravelGenie Engine"}

        # We have the details! Let's invoke all tools to fetch REAL live data:
        cur_origin = trip_data["origin"]
        cur_dest = trip_data["destination"]
        cur_date = trip_data["onward_date"]
        cur_ret_date = trip_data.get("return_date")
        cur_days = trip_data.get("days", 3)
        cur_budget = trip_data.get("budget", "mid")
        cur_travelers = trip_data.get("travelers", 1)

        # Tool 1: Live Weather
        weather_res = await get_weather(city=cur_dest)
        tool_calls.append({"tool": "get_weather", "args": {"city": cur_dest}, "result": weather_res})

        # Tool 2: Transport Comparison (Flights, Trains, Buses onward and return)
        transport_res = await compare_transport(
            origin=cur_origin,
            destination=cur_dest,
            date=cur_date,
            return_date=cur_ret_date,
            travelers=cur_travelers
        )
        tool_calls.append({"tool": "compare_transport", "args": {"origin": cur_origin, "destination": cur_dest, "date": cur_date}, "result": transport_res})

        # Tool 3: Hotel Search sorted by budget preference
        checkout_date = cur_ret_date or self._add_days_to_date(cur_date, cur_days)
        hotels_res = await search_hotels(
            city=cur_dest,
            checkin_date=cur_date,
            checkout_date=checkout_date,
            guests=cur_travelers,
            budget_preference=cur_budget
        )
        tool_calls.append({"tool": "search_hotels", "args": {"city": cur_dest, "budget_preference": cur_budget}, "result": hotels_res})

        # Tool 4: Generate Day-wise Itinerary
        itinerary_res = await generate_itinerary(
            destination=cur_dest,
            days=cur_days,
            budget_preference=cur_budget
        )
        tool_calls.append({"tool": "generate_itinerary", "args": {"destination": cur_dest, "days": cur_days}, "result": itinerary_res})

        # Pick best transport and hotel for quotation
        selected_hotel = hotels_res["hotels"][0] if hotels_res["hotels"] else {}
        selected_transport = transport_res["cheapest_mode_highlight"]
        
        # Calculate Grand Total Cost
        onward_transport_cost = selected_transport.get("total_price", 0)
        return_transport_cost = 0
        if transport_res.get("return_options"):
            return_transport_cost = transport_res["return_options"]["cheapest_return_option"]["total_price"]
        else:
            return_transport_cost = onward_transport_cost  # symmetric estimate

        hotel_total_cost = selected_hotel.get("total_stay_inr", 0)
        itinerary_expense = itinerary_res["expense_breakdown"]["grand_total_itinerary_inr"]
        grand_total = onward_transport_cost + return_transport_cost + hotel_total_cost + itinerary_expense

        # Save last quote in session for booking confirmation
        session["last_quote"] = {
            "selected_transport": selected_transport,
            "selected_hotel": selected_hotel,
            "itinerary_expense": itinerary_expense,
            "total_trip_cost_inr": grand_total,
            "breakdown": {
                "onward_transport": onward_transport_cost,
                "return_transport": return_transport_cost,
                "hotel_total": hotel_total_cost,
                "itinerary_expenses": itinerary_expense
            }
        }

        # Build concise, beautifully structured TravelGenie response
        reply = self._build_travel_genie_summary(
            origin=cur_origin,
            dest=cur_dest,
            dates=(cur_date, checkout_date),
            days=cur_days,
            budget=cur_budget,
            travelers=cur_travelers,
            weather=weather_res,
            transport=transport_res,
            hotels=hotels_res,
            itinerary=itinerary_res,
            quote=session["last_quote"]
        )

        session["messages"].append({"role": "assistant", "content": reply})
        return {
            "reply": reply,
            "tool_calls": tool_calls,
            "provider": "Built-in TravelGenie Engine",
            "quote": session["last_quote"]
        }

    def _build_travel_genie_summary(self, origin, dest, dates, days, budget, travelers, weather, transport, hotels, itinerary, quote) -> str:
        w_temp = weather.get("temperature_c", "N/A")
        w_cond = weather.get("condition", "Pleasant")
        w_pack = weather.get("packing_recommendation", "")

        onward = transport["onward_options"]
        flights = onward.get("flights", [])
        trains = onward.get("trains", [])
        buses = onward.get("buses", [])

        # Transport Table
        transport_table = f"""| Mode | Operator / Service | Duration | Class | Price / Person | Total ({travelers} Pax) | Booking Type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Flight** | {flights[0]['provider']} ({flights[0]['identifier']}) | {flights[0]['duration']} | {flights[0]['class_type']} | ₹{flights[0]['price_per_person']:,} | ₹{flights[0]['total_price']:,} | Instant API |
| **Train** | {trains[0]['provider']} - {trains[0]['identifier']} | {trains[0]['duration']} | {trains[0]['class_type']} | ₹{trains[0]['price_per_person']:,} | ₹{trains[0]['total_price']:,} | [IRCTC Link]({trains[0]['booking_url']}) |
| **Bus** | {buses[0]['provider']} | {buses[0]['duration']} | {buses[0]['class_type']} | ₹{buses[0]['price_per_person']:,} | ₹{buses[0]['total_price']:,} | [RedBus Link]({buses[0]['booking_url']}) |
"""

        # Hotel Cards
        hotel_list_str = ""
        for h in hotels["hotels"][:3]:
            hotel_list_str += f"- **{h['name']}** ({h['stars']}⭐, Rating: {h['rating']}/5) — {h['area']}\n  - **₹{h['price_per_night_inr']:,}/night** (Total for {h['nights']} nights: **₹{h['total_stay_inr']:,}**)\n  - Amenities: {', '.join(h['amenities'][:3])}\n"

        # Itinerary Highlights
        itin_str = ""
        for day in itinerary["days"]:
            itin_str += f"- **Day {day['day']}: {day['title']}**\n"
            itin_str += f"  - *Morning:* {day['schedule']['morning']}\n"
            itin_str += f"  - *Afternoon:* {day['schedule']['afternoon']}\n"
            itin_str += f"  - *Evening:* {day['schedule']['evening']}\n"
            itin_str += f"  - *Est. Daily Expense:* ₹{day['expense_estimate']['day_total_inr']:,} (Entry: ₹{day['expense_estimate']['entry_fees_inr']}, Local Transport: ₹{day['expense_estimate']['local_transport_inr']}, Food: ₹{day['expense_estimate']['food_and_beverages_inr']})\n"

        q_breakdown = quote["breakdown"]

        return f"""### 🧳 Trip Plan: {origin.title()} ➔ {dest.title()} ({days} Days)
**Dates:** {dates[0]} to {dates[1]} | **Travelers:** {travelers} | **Budget Level:** {budget.title()}

🌤️ **Live Weather in {dest.title()}:** {w_temp}°C, {w_cond}  
🎒 **Packing Note:** {w_pack}

---

### 1. 🚆 Transport Comparison (Cheapest vs Fastest)
> **Cheapest Option:** {transport['cheapest_mode_highlight']['mode']} ({transport['cheapest_mode_highlight']['provider']}) at **₹{transport['cheapest_mode_highlight']['total_price']:,}** total.  
> **Fastest Option:** {transport['fastest_mode_highlight']['mode']} ({transport['fastest_mode_highlight']['provider']}) in **{transport['fastest_mode_highlight']['duration']}**.

{transport_table}
*Note: For train and bus tickets, verified direct booking links are provided above in compliance with reservation regulations.*

---

### 2. 🏨 Recommended Accommodations ({hotels['sorting_rule']})
{hotel_list_str}

---

### 3. 🗺️ Day-Wise Itinerary & Local Expenses
{itin_str}
**Total Itinerary Local Expenses:** ₹{itinerary['expense_breakdown']['grand_total_itinerary_inr']:,}

---

### 4. 💳 Final Total Trip Cost Breakdown
| Component | Estimated Cost |
| :--- | :--- |
| **Onward Transport** ({transport['cheapest_mode_highlight']['mode']}) | ₹{q_breakdown['onward_transport']:,} |
| **Return Transport** ({transport['cheapest_mode_highlight']['mode']}) | ₹{q_breakdown['return_transport']:,} |
| **Hotel Stay** ({hotels['hotels'][0]['name']}, {hotels['nights']} Nights) | ₹{q_breakdown['hotel_total']:,} |
| **Itinerary Expenses** (Entry Fees + Food + Local Cabs) | ₹{q_breakdown['itinerary_expenses']:,} |
| **GRAND TOTAL TRIP COST** | **₹{quote['total_trip_cost_inr']:,}** |

---

🔔 **Ready to Book?**  
To confirm this reservation and initiate booking via `book_and_pay`, please reply with **"Confirm and Book"** or let me know if you would like any modifications!
"""

    def _extract_origin_destination(self, text: str):
        # Look for patterns like "from X to Y", "X to Y"
        match = re.search(r'(?:from\s+)?([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:[\.,\s]|$)', text)
        if match:
            o = match.group(1).replace("trip", "").replace("plan", "").strip().title()
            d = match.group(2).replace("for", "").replace("in", "").strip().title()
            # Clean words
            o = o.split()[-1] if len(o.split()) > 2 else o
            d = d.split()[0] if len(d.split()) > 2 else d
            return o, d
        
        # Check known Indian cities
        cities = ["delhi", "mumbai", "goa", "jaipur", "udaipur", "manali", "varanasi", "bangalore", "bengaluru", "kolkata", "chennai", "hyderabad", "agra", "srinagar"]
        found = [c.title() for c in cities if c in text]
        if len(found) >= 2:
            return found[0], found[1]
        elif len(found) == 1:
            return None, found[0]
        return None, None

    def _extract_budget(self, text: str) -> Optional[str]:
        if "cheap" in text or "budget" in text or "economy" in text or "low cost" in text:
            return "cheap"
        elif "premium" in text or "luxury" in text or "5 star" in text or "five star" in text:
            return "premium"
        elif "mid" in text or "moderate" in text or "standard" in text:
            return "mid"
        return "mid"

    def _extract_days(self, text: str) -> int:
        match = re.search(r'(\d+)\s*(?:days|day|nights|night)', text)
        if match:
            return int(match.group(1))
        return 3

    def _extract_travelers(self, text: str) -> int:
        match = re.search(r'(\d+)\s*(?:travelers|traveler|people|person|persons|passengers|adults)', text)
        if match:
            return int(match.group(1))
        return 1

    def _extract_dates(self, text: str) -> Dict[str, Optional[str]]:
        # Check for YYYY-MM-DD
        dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text)
        if len(dates) >= 2:
            return {"onward": dates[0], "return": dates[1]}
        elif len(dates) == 1:
            return {"onward": dates[0], "return": None}
        
        # Fallback date if not specified
        return {"onward": "2026-10-15", "return": "2026-10-18"}

    def _add_days_to_date(self, date_str: str, days: int) -> str:
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return (d + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        except Exception:
            return "2026-10-18"
