"""
Weather context service using Open-Meteo API.
Fetches real-time weather data as contextual signals for demand forecasting.
"""

import httpx
from typing import Optional
from app.config import get_settings


PINCODE_COORDS = {
    "400053": (19.1136, 72.8697),
    "400050": (19.0596, 72.8295),
    "110001": (28.6315, 77.2167),
    "110024": (28.5700, 77.2373),
    "560034": (12.9352, 77.6245),
    "560038": (12.9716, 77.6412),
    "500081": (17.4435, 78.3772),
    "600017": (13.0418, 80.2341),
    "411001": (18.5362, 73.8939),
    "700016": (22.5495, 88.3514),
}


def _weather_code_to_condition(code: int) -> str:
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }
    return mapping.get(code, "Unknown")


async def fetch_weather(latitude: float, longitude: float) -> Optional[dict]:
    """Fetch current + hourly forecast weather from Open-Meteo."""
    settings = get_settings()
    url = f"{settings.open_meteo_base_url}/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "hourly": "temperature_2m,weather_code,precipitation_probability",
        "forecast_days": 2,
        "timezone": "Asia/Kolkata",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            hourly = data.get("hourly", {})

            return {
                "current": {
                    "temperature": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "condition": _weather_code_to_condition(current.get("weather_code", 0)),
                    "wind_speed": current.get("wind_speed_10m"),
                },
                "hourly_temperatures": hourly.get("temperature_2m", [])[:48],
                "hourly_conditions": [
                    _weather_code_to_condition(c) for c in hourly.get("weather_code", [])[:48]
                ],
                "hourly_precipitation_prob": hourly.get("precipitation_probability", [])[:48],
                "hourly_times": hourly.get("time", [])[:48],
            }
    except Exception as e:
        print(f"[Weather] Failed to fetch weather data: {e}")
        return None


async def get_weather_for_pincode(pincode: str) -> Optional[dict]:
    coords = PINCODE_COORDS.get(pincode)
    if not coords:
        return None
    return await fetch_weather(coords[0], coords[1])


def get_coords_for_pincode(pincode: str) -> Optional[tuple]:
    return PINCODE_COORDS.get(pincode)
