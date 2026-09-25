# 🧳 TravelGenie - AI Travel Planning & Booking Assistant for Indian Domestic Travel

**TravelGenie** is a specialized, production-ready AI Travel Agent built for Indian domestic travel. It plans comprehensive journeys, compares live multi-modal transport (Flights, Trains via IRCTC, and Intercity Buses), recommends verified hotels based on budget preferences, builds day-wise itineraries with realistic daily local expenses, and securely facilitates booking with explicit confirmation checks.

---

## 🌟 Key Features & Workflow

1. **Intelligent Trip Intake**: Understands origin, destination, travel dates, trip duration, number of travelers, and budget preference (*Cheap*, *Mid*, *Premium*).
2. **Real Data Enforcement**: Integrates real live meteorological and transport data. Never invents prices, flight numbers, or hotel names.
3. **Multi-Modal Transport Comparison**:
   - Compares **Flights** (IndiGo, Air India, Akasa Air) with instant confirmation.
   - Compares **Indian Railways (IRCTC)** (Vande Bharat, Rajdhani, Superfast Express) with verified direct IRCTC reservation links.
   - Compares **Intercity Buses** (IntrCity, Zingbus, NueGo, State RTCs) with direct booking links.
   - Clearly flags **Cheapest Option** vs **Fastest Option**.
4. **Budget-Preference Hotel Ranking**:
   - `cheap`: Sorted strictly by lowest price first.
   - `premium`: Sorted strictly by highest rating and 5-star luxury heritage properties first.
   - `mid`: Curated 3–4 star high-value properties.
5. **Day-Wise Itinerary & Expense Calculator**:
   - Real attractions grouped geographically with morning, afternoon, and evening schedules.
   - Daily breakdown of entry fees + local transport (auto/cab) + food expenses.
6. **Total Trip Cost Estimation**:
   - `Onward Transport + Hotel Total + Daily Itinerary Expenses + Return Transport`.
7. **Strict Booking Confirmation Policy**:
   - Pre-presents the full summary before requesting confirmation.
   - Calls `book_and_pay` **only** upon explicit user confirmation, generating confirmed PNR/hotel vouchers or direct reservation links.

---

## 🛠️ Available Tools

| Tool | Description |
| :--- | :--- |
| `compare_transport` | Compares Flights, Trains (IRCTC), and Buses for onward & return journeys. |
| `search_hotels` | Fetches verified Indian hotels with budget-based sorting. |
| `get_weather` | Fetches live weather, temperatures, and packing advice using Open-Meteo & OpenWeatherMap. |
| `get_place_info` | Provides opening hours, visitor timings, and entry fees (Indian vs Foreign). |
| `generate_itinerary` | Builds day-wise attraction itineraries with estimated daily expenses. |
| `book_and_pay` | Authorized payment and reservation execution with strict confirmation safeguards. |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Virtual environment (already configured in `venv/`)

### 2. Configure Environment Variables (Optional)
Copy `.env.example` to `.env` and set your preferred LLM or external keys:
```bash
copy .env.example .env
```
Supported Keys:
- `GEMINI_API_KEY`: For Google Gemini 2.5 Flash / Pro.
- `OPENAI_API_KEY`: For OpenAI GPT-4o / GPT-4o-mini.
- `OPENWEATHER_API_KEY`: Optional OpenWeather key (Open-Meteo works live out of the box without keys).

*(Note: If no API key is provided, TravelGenie's built-in autonomous planning engine runs seamlessly using live data).*

### 3. Run the Application
```powershell
.\venv\Scripts\python run.py
```
Open your browser at:
- **Interactive Web Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Running the Test Suite

Execute the automated test suite covering all tools and the agent workflow:
```powershell
.\venv\Scripts\python tests/test_tools.py
```

---

## 📡 REST API Endpoints

- `POST /api/chat`: Multi-turn conversational endpoint with session memory.
- `POST /api/tools/compare_transport`: Compare flight, train, and bus options.
- `POST /api/tools/search_hotels`: Search and rank accommodations.
- `POST /api/tools/get_weather`: Fetch real live weather and packing advice.
- `POST /api/tools/get_place_info`: Retrieve monument timings and ticket prices.
- `POST /api/tools/generate_itinerary`: Generate day-wise schedules with expense estimates.
- `POST /api/tools/book_and_pay`: Execute authorized booking with explicit confirmation.
- `GET /api/health`: Health status and configured providers.
