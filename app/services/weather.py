import httpx
from typing import Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.base_url = settings.OPEN_METEO_URL
        self.default_params = {
            "latitude": settings.LATITUDE,
            "longitude": settings.LONGITUDE,
            "current": ["temperature_2m", "relative_humidity_2m", 
                       "wind_speed_10m"],
            "timezone": "UTC"
        }
    
    async def fetch_current_weather(self) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=self.default_params)
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current", {})
                
                return {
                    "location": f"{settings.LATITUDE},{settings.LONGITUDE}",
                    "temperature": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "wind_speed": current.get("wind_speed_10m"),
                }
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None