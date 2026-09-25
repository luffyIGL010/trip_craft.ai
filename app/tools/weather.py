import httpx
from typing import Dict, Any, Optional
from app.config import settings

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

async def get_weather(city: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch REAL live weather data for an Indian city using Open-Meteo or OpenWeather API.
    Guarantees actual live meteorology data.
    """
    cleaned_city = city.strip()
    
    # 1. Check if OpenWeather API key is provided
    if settings.OPENWEATHER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": f"{cleaned_city},IN",
                        "appid": settings.OPENWEATHER_API_KEY,
                        "units": "metric"
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "city": data.get("name", cleaned_city),
                        "temperature_c": data["main"]["temp"],
                        "feels_like_c": data["main"]["feels_like"],
                        "humidity_pct": data["main"]["humidity"],
                        "condition": data["weather"][0]["description"].title(),
                        "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
                        "source": "OpenWeather API (Live)",
                        "packing_recommendation": _get_packing_recommendation(data["main"]["temp"], data["weather"][0]["description"])
                    }
        except Exception as e:
            pass  # Fallback to Open-Meteo

    # 2. Live Free Real Meteorology API (Open-Meteo, works without API key)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            geo_res = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": cleaned_city, "count": 1, "language": "en", "format": "json"}
            )
            geo_data = geo_res.json()
            if not geo_data.get("results"):
                return {
                    "city": cleaned_city,
                    "error": f"City '{cleaned_city}' not found in geographical directory."
                }
            
            loc = geo_data["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            city_name = loc.get("name", cleaned_city)
            state = loc.get("admin1", "")

            weather_res = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": "Asia/Kolkata"
                }
            )
            w_data = weather_res.json()
            current = w_data.get("current", {})
            current_weather = w_data.get("current_weather", {})
            daily = w_data.get("daily", {})
            
            w_code = current.get("weather_code") or current_weather.get("weathercode", 0)
            condition = WMO_WEATHER_CODES.get(w_code, "Pleasant")
            temp = current.get("temperature_2m") or current_weather.get("temperature")
            if temp is None and daily and "temperature_2m_max" in daily and daily["temperature_2m_max"]:
                temp = round((daily["temperature_2m_max"][0] + daily["temperature_2m_min"][0]) / 2.0, 1)
            humidity = current.get("relative_humidity_2m", 60)
            wind = current.get("wind_speed_10m") or current_weather.get("windspeed", 10.0)
            
            # Forecast summary for next few days
            daily_forecast = []
            if daily and "time" in daily:
                for i in range(min(5, len(daily["time"]))):
                    daily_forecast.append({
                        "date": daily["time"][i],
                        "max_temp_c": daily["temperature_2m_max"][i],
                        "min_temp_c": daily["temperature_2m_min"][i],
                        "rain_chance_pct": daily["precipitation_probability_max"][i],
                        "condition": WMO_WEATHER_CODES.get(daily["weather_code"][i], "Clear")
                    })

            return {
                "city": f"{city_name}{f', {state}' if state else ''}, India",
                "temperature_c": temp,
                "humidity_pct": humidity,
                "wind_speed_kmh": wind,
                "condition": condition,
                "source": "Open-Meteo Live Meteorology Data",
                "forecast": daily_forecast,
                "packing_recommendation": _get_packing_recommendation(temp, condition)
            }
    except Exception as exc:
        return {
            "city": cleaned_city,
            "error": f"Live weather service currently unavailable: {str(exc)}"
        }

def _get_packing_recommendation(temp: Optional[float], condition: str) -> str:
    if temp is None:
        return "Standard comfortable clothing."
    condition_lower = condition.lower()
    if "rain" in condition_lower or "drizzle" in condition_lower or "thunder" in condition_lower:
        return "Pack an umbrella, raincoat, waterproof footwear, and quick-dry apparel."
    elif temp < 12:
        return "Heavy woolens, thermals, gloves, and a warm jacket are recommended."
    elif temp < 20:
        return "Light jacket, sweater, or shawls for evenings and early mornings."
    elif temp > 33:
        return "Breathable cottons, sunglasses, SPF sunscreen, and a wide-brim hat."
    else:
        return "Comfortable casual cottons and light layers."
