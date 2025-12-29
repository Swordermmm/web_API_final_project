from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WeatherBase(BaseModel):
    location: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None


class WeatherUpdate(BaseModel):
    location: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None


class WeatherResponse(WeatherBase):
    id: int
    
    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    message: str
    task_id: Optional[str] = None


class WebSocketMessage(BaseModel):
    type: str
    data: dict


class OpenMeteoResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_units: dict
    current: dict