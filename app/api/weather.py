from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.db.db import get_session
from app.models.models import WeatherHistory
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current")
async def get_current_weather():
    service = WeatherService()
    weather = await service.fetch_current_weather()
    return weather


@router.get("/history")
async def get_weather_history(
    hours: int = 24,
    session: AsyncSession = Depends(get_session)
):
    since = datetime.now() - timedelta(hours=hours)
    
    stmt = select(WeatherHistory).where(
        WeatherHistory.recorded_at >= since
    ).order_by(WeatherHistory.recorded_at.desc())
    
    result = await session.execute(stmt)
    history = result.scalars().all()
    
    return [h.to_dict() for h in history]