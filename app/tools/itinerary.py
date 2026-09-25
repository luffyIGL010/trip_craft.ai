from typing import Dict, Any, List, Optional

DESTINATION_ITINERARY_TEMPLATES = {
    "goa": [
        {
            "day": 1,
            "title": "North Goa Beaches & Sunset Buzz",
            "morning": "Arrival, check-in, and relax with authentic Goan breakfast (Poi & Chorizo/Bhaji). Visit Sinquerim Beach & Aguada Fort lighthouse.",
            "afternoon": "Lunch at a beachfront shack in Candolim. Explore Calangute and Baga Beach shores.",
            "evening": "Stroll down Tito's Lane, catch the fiery Arabian Sea sunset at Curlies/Shiva Valley (Anjuna), and enjoy fresh seafood dinner.",
            "costs": {"entry_fees": 100, "local_transport": 700, "food_and_drinks": 1100}
        },
        {
            "day": 2,
            "title": "Heritage Old Goa & Panaji Latin Quarter",
            "morning": "UNESCO Heritage trail in Old Goa: Visit Basilica of Bom Jesus, Se Cathedral, and Church of St. Francis of Assisi.",
            "afternoon": "Head to Panaji. Traditional Goan Thali lunch at Ritz Classic or Viva Panjim. Explore colourful Portuguese alleys of Fontainhas.",
            "evening": "Sunset Mandovi River Cruise with Goan folk dance performances or seaside dinner along Miramar Beach.",
            "costs": {"entry_fees": 150, "local_transport": 650, "food_and_drinks": 1200}
        },
        {
            "day": 3,
            "title": "South Goa Serenity & Scenic Cliffs",
            "morning": "Drive south to Cabo de Rama Fort perched over pristine turquoise waters. Relax at Cola Beach lagoon.",
            "afternoon": "Leisurely lunch at Palolem Beach. Kayaking in the tranquil backwaters or sea dolphin boat tour.",
            "evening": "Sunset at Agonda Beach, beachside candlelit barbecue dinner with live acoustic music.",
            "costs": {"entry_fees": 50, "local_transport": 900, "food_and_drinks": 1300}
        },
        {
            "day": 4,
            "title": "Waterfalls & Spice Plantation Safari",
            "morning": "Full day excursion: Dudhsagar Falls Jeep Safari through Mollem National Park. Dip in natural plunge pools.",
            "afternoon": "Traditional Goan buffet lunch served on banana leaves at Sahakari Spice Farm, followed by spice tour and betel nut climbing demo.",
            "evening": "Return to your hotel, relax by the pool, and enjoy an evening night market (Anjuna Flea Market / Arpora Saturday Night Market if in season).",
            "costs": {"entry_fees": 750, "local_transport": 800, "food_and_drinks": 600}
        },
        {
            "day": 5,
            "title": "Flea Markets, Cafes & Souvenir Shopping",
            "morning": "Brunch at Artjuna or Baba Au Rhum. Browse boutique shops in Vagator and Assagao.",
            "afternoon": "Visit Chapora Fort ('Dil Chahta Hai' viewpoint) overlooking the Ozran coast.",
            "evening": "Farewell sunset drinks at Thalassa (Siolim) or Purple Martini (Anjuna) with sunset views.",
            "costs": {"entry_fees": 50, "local_transport": 600, "food_and_drinks": 1400}
        }
    ],
    "jaipur": [
        {
            "day": 1,
            "title": "Heart of the Pink City: Forts & Palaces",
            "morning": "Early visit to iconic Amber Fort & Palace (Amer). Walk through the breathtaking Sheesh Mahal (Mirror Palace) and Maota Lake.",
            "afternoon": "Stop at Jal Mahal (Water Palace) for photos. Authentic Rajasthani Thali lunch at 1135 AD or LMB (Laxmi Mishtan Bhandar).",
            "evening": "Explore the royal courtyards of City Palace and UNESCO-listed Jantar Mantar observatory. Evening tea overlooking Hawa Mahal.",
            "costs": {"entry_fees": 450, "local_transport": 500, "food_and_drinks": 900}
        },
        {
            "day": 2,
            "title": "Hilltop Fortresses & Artisan Bazaars",
            "morning": "Visit Jaigarh Fort (housing the world's largest wheeled cannon Jaivana) and continue to Nahargarh Fort.",
            "afternoon": "Panoramic lunch overlooking the entire Jaipur skyline at Padao Cafe (Nahargarh). Visit Albert Hall Museum.",
            "evening": "Shopping walk through Johari Bazaar (gemstones & jewelry) and Bapu Bazaar (Jaipuri quilts & mojris). Street food: Pyaaz Kachori at Rawat Mishtan.",
            "costs": {"entry_fees": 300, "local_transport": 550, "food_and_drinks": 800}
        },
        {
            "day": 3,
            "title": "Cultural Village & Royal Stepwells",
            "morning": "Visit the mesmerizing geometric architecture of Chand Baori Stepwell or Panna Meena Ka Kund.",
            "afternoon": "Visit Galtaji Temple (Monkey Temple) and Royal Gaitor Chhatris. Traditional Laal Maas lunch at Handi.",
            "evening": "Immersive cultural evening at Chokhi Dhani ethnic village resort with camel rides, puppet shows, folk Kalbelia dances, and royal dining.",
            "costs": {"entry_fees": 850, "local_transport": 700, "food_and_drinks": 1000}
        },
        {
            "day": 4,
            "title": "Heritage Haveli Craft & Royal Gardens",
            "morning": "Visit Sisodia Rani Garden and Kanak Vrindavan Valley at the foot of Nahargarh hills.",
            "afternoon": "Block-printing workshop and textile museum tour at Anokhi Museum of Hand Printing in Amber.",
            "evening": "Sunset high tea at Nahargarh Fort or Peacock Rooftop Restaurant. Packing and departure prep.",
            "costs": {"entry_fees": 200, "local_transport": 500, "food_and_drinks": 950}
        }
    ],
    "varanasi": [
        {
            "day": 1,
            "title": "Sacred Ghats & Ganga Aarti",
            "morning": "Arrival, check-in. Morning walk along Assi Ghat. Enjoy hot Kulhad Chai and famous Banarasi Kachori-Jalebi at Ram Bhandar.",
            "afternoon": "Visit Banaras Hindu University (BHU) campus and the New Vishwanath Temple (Birla Temple).",
            "evening": "Grand Evening Ganga Aarti at Dashashwamedh Ghat viewed from a traditional wooden boat. Authentic dinner at Baati Chokha.",
            "costs": {"entry_fees": 350, "local_transport": 400, "food_and_drinks": 700}
        },
        {
            "day": 2,
            "title": "Sunrise Boat Ride & Spiritual Corridors",
            "morning": "05:30 AM Sunrise rowing boat tour from Assi Ghat to Manikarnika Ghat. Darshan at Kashi Vishwanath Temple corridor & Annapurna Temple.",
            "afternoon": "Wander through the historic alleys (galis), taste famous Blue Lassi and Banarasi Paan. Visit Kaal Bhairav temple.",
            "evening": "Explore local silk weaving quarters to watch Banarasi sarees woven on traditional handlooms.",
            "costs": {"entry_fees": 300, "local_transport": 350, "food_and_drinks": 750}
        },
        {
            "day": 3,
            "title": "Buddhist Heritage at Sarnath",
            "morning": "Excursion to Sarnath (where Lord Buddha gave his first sermon). Visit Dhamek Stupa and Ashoka Pillar.",
            "afternoon": "Explore the Sarnath Archaeological Museum (houses the original Lion Capital of Ashoka). Lunch at a serene garden restaurant.",
            "evening": "Sunset meditation at Thai Temple or Tibetan Monastery in Sarnath before returning to city center.",
            "costs": {"entry_fees": 250, "local_transport": 600, "food_and_drinks": 650}
        }
    ],
    "manali": [
        {
            "day": 1,
            "title": "Old Manali Vibe & Sacred Cedar Forests",
            "morning": "Arrival, check-in. Walk to Hadimba Devi Temple set amidst towering deodar cedars. Visit Ghatotkach Tree Temple.",
            "afternoon": "Lunch at Cafe 1947 or Dylan's Toasted & Roasted in Old Manali. Walk to Manu Temple.",
            "evening": "Stroll down Mall Road and Tibetan Monastery. Taste local Trout fish and Siddu (steamed Himachali bun).",
            "costs": {"entry_fees": 50, "local_transport": 400, "food_and_drinks": 950}
        },
        {
            "day": 2,
            "title": "Snow Peaks, Ropeways & Solang Valley",
            "morning": "Drive to Solang Valley. Enjoy thrilling adventure sports (ropeway cable car ride, paragliding, or quad biking).",
            "afternoon": "Himachali lunch at Solang. Drive through the engineering marvel Atal Tunnel into Lahaul Valley.",
            "evening": "Witness the frozen or roaring Sissu Waterfall. Warm up with hot thukpa and momos. Return to Manali.",
            "costs": {"entry_fees": 1200, "local_transport": 900, "food_and_drinks": 850}
        },
        {
            "day": 3,
            "title": "Hot Springs of Vashisht & Jogini Waterfalls",
            "morning": "Visit Vashisht Village, take a holy dip in natural sulfur hot springs. Scenic 1-hour forest trek to Jogini Waterfall.",
            "afternoon": "Picnic lunch near Jogini cascades. Visit Nehru Kund and Club House for indoor activities.",
            "evening": "Bonfire night and riverside live music at your resort or Old Manali cafe.",
            "costs": {"entry_fees": 100, "local_transport": 450, "food_and_drinks": 900}
        }
    ]
}

def _get_budget_multiplier(budget_preference: str) -> float:
    b = budget_preference.lower()
    if b == "cheap":
        return 0.75  # Street food, public autos/buses, budget dining
    elif b == "premium":
        return 1.75  # Fine dining, private AC cab throughout, premium VIP access
    return 1.0  # Balanced mid-range

async def generate_itinerary(
    destination: str,
    days: int,
    budget_preference: str = "mid",
    interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Builds a day-wise itinerary using verified attractions for the destination city,
    with realistic estimated daily expenses (entry fees + local transport + food).
    """
    dest_clean = destination.lower().strip()
    multiplier = _get_budget_multiplier(budget_preference)

    # Check template database
    templates = None
    for key, days_data in DESTINATION_ITINERARY_TEMPLATES.items():
        if key in dest_clean or dest_clean in key:
            templates = days_data
            break

    itinerary_days = []
    total_entry_fees = 0
    total_transport = 0
    total_food = 0

    actual_days = max(1, min(days, 14))

    for day_num in range(1, actual_days + 1):
        if templates and (day_num - 1) < len(templates):
            t = templates[day_num - 1]
            title = t["title"]
            morning = t["morning"]
            afternoon = t["afternoon"]
            evening = t["evening"]
            base_costs = t["costs"]
        else:
            # Dynamically construct tailored day
            title = f"Exploring {destination.title()} - Discovery & Highlights Part {day_num}"
            morning = f"Morning sightseeing at prominent landmarks and cultural sights in {destination.title()}."
            afternoon = f"Lunch at a celebrated local restaurant. Visit top artisan markets and historic centers."
            evening = f"Sunset viewpoint or scenic lakeside/promenade walk followed by local culinary dinner."
            base_costs = {"entry_fees": 200, "local_transport": 600, "food_and_drinks": 900}

        entry_cost = int(base_costs["entry_fees"] * (1.2 if budget_preference == "premium" else 0.9 if budget_preference == "cheap" else 1.0))
        transport_cost = int(base_costs["local_transport"] * multiplier)
        food_cost = int(base_costs["food_and_drinks"] * multiplier)
        day_total = entry_cost + transport_cost + food_cost

        total_entry_fees += entry_cost
        total_transport += transport_cost
        total_food += food_cost

        itinerary_days.append({
            "day": day_num,
            "title": title,
            "schedule": {
                "morning": morning,
                "afternoon": afternoon,
                "evening": evening
            },
            "expense_estimate": {
                "entry_fees_inr": entry_cost,
                "local_transport_inr": transport_cost,
                "food_and_beverages_inr": food_cost,
                "day_total_inr": day_total
            }
        })

    grand_total_itinerary = total_entry_fees + total_transport + total_food

    return {
        "destination": destination.title(),
        "duration_days": actual_days,
        "budget_preference": budget_preference,
        "expense_breakdown": {
            "total_entry_fees_inr": total_entry_fees,
            "total_local_transport_inr": total_transport,
            "total_food_and_beverages_inr": total_food,
            "grand_total_itinerary_inr": grand_total_itinerary,
            "average_daily_cost_inr": int(grand_total_itinerary / actual_days)
        },
        "days": itinerary_days,
        "traveler_tips": [
            "Local auto-rickshaws often run on meter or fixed tourist cards; negotiate beforehand or use Ola/Uber where active.",
            "Bottled or purified water is advised throughout your excursion.",
            "Keep small denomination Indian Rupee notes (₹10, ₹20, ₹50, ₹100) and UPI handy for temples and street vendors."
        ]
    }
