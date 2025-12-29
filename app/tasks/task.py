import asyncio
import logging
from typing import Optional
from sqlalchemy import select

from app.db.db import async_session_maker
from app.models.models import WeatherItem, WeatherHistory
from app.services.weather import WeatherService
from app.nats.client import NATSService
from app.config import settings
from app.ws.websocket import manager

logger = logging.getLogger(__name__)

class BackgroundTask:
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.weather_service = WeatherService()
        self.interval = settings.BACKGROUND_TASK_INTERVAL
    
    async def start(self):
        if self.is_running:
            logger.warning("Background task is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_periodically())
        logger.info("Background task started")
    
    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Background task stopped")
    
    async def run_once(self):
        logger.info("Running background task manually")
        await self._fetch_and_process_weather()
    
    async def _run_periodically(self):
        while self.is_running:
            try:
                await self._fetch_and_process_weather()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                await asyncio.sleep(self.interval)
    
    async def _fetch_and_process_weather(self):
        try:
            weather_data = await self.weather_service.fetch_current_weather()
            
            if not weather_data:
                logger.warning("No weather data received")
                return
            
            async with async_session_maker() as session:
                stmt = select(WeatherItem).where(
                    WeatherItem.location == weather_data["location"]
                )
                result = await session.execute(stmt)
                item = result.scalar_one_or_none()
                
                if item:
                    item.temperature = weather_data["temperature"]
                    item.humidity = weather_data["humidity"]
                    item.wind_speed = weather_data["wind_speed"]
                else:
                    item = WeatherItem(
                        location=weather_data["location"],
                        temperature=weather_data["temperature"],
                        humidity=weather_data["humidity"],
                        wind_speed=weather_data["wind_speed"],
                    )
                    session.add(item)
                
                await session.commit()
                await session.refresh(item)
                
                history = WeatherHistory(
                    location=weather_data["location"],
                    temperature=weather_data["temperature"],
                    humidity=weather_data["humidity"],
                    wind_speed=weather_data["wind_speed"],
                )
                session.add(history)
                await session.commit()
                
                await NATSService.publish_weather_data(item.to_dict())
                
                await manager.broadcast_item_update("created", item.to_dict())
                logger.info(f"Weather data updated for {weather_data['location']}")
                
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")


background_task = BackgroundTask()