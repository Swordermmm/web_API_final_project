import asyncio
import json
import logging
from typing import Optional
from nats.aio.client import Client as NATS
from app.config import settings

logger = logging.getLogger(__name__)

# Клиент NATS 
class NATSClient:
    def __init__(self):
        self.nc: Optional[NATS] = None
        self.is_connected = False
    
    async def connect(self):
        try:
            self.nc = NATS()
            await self.nc.connect(servers=[settings.NATS_URL])
            self.is_connected = True
            logger.info(f"Connected to NATS at {settings.NATS_URL}")
            
            await self.subscribe_items()
            
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        if self.nc and self.is_connected:
            await self.nc.drain()
            await self.nc.close()
            self.is_connected = False
            logger.info("Disconnected from NATS")
    
    async def publish(self, subject: str, message: dict):
        if not self.nc or not self.is_connected:
            logger.warning("NATS not connected, skipping publish")
            return
        
        try:
            await self.nc.publish(
                subject,
                json.dumps(message).encode()
            )
            logger.debug(f"Published to {subject}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to NATS: {e}")
    
    async def subscribe_items(self):
        if not self.nc or not self.is_connected:
            return
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                logger.info(f"Received NATS message from {msg.subject}: {data}")
                
            except Exception as e:
                logger.error(f"Error processing NATS message: {e}")
        
        await self.nc.subscribe(
            settings.NATS_TOPIC_ITEMS,
            cb=message_handler
        )

        await self.nc.subscribe(
            settings.NATS_TOPIC_WEATHER,
            cb=message_handler
        )
    
    async def publish_item_update(self, item_id: int, action: str, data: dict):
        message = {
            "action": action,
            "item_id": item_id,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.publish(settings.NATS_TOPIC_ITEMS, message)
    
    async def publish_weather_update(self, weather_data: dict):
        message = {
            "type": "weather_update",
            "data": weather_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.publish(settings.NATS_TOPIC_WEATHER, message)

nats_client = NATSClient()

from typing import Dict, Any

# Сервис NATS
class NATSService:
    @staticmethod
    async def publish_item_created(item_id: int, item_data: Dict[str, Any]):
        await nats_client.publish_item_update(
            item_id, 
            "created", 
            item_data
        )
    
    @staticmethod
    async def publish_item_updated(item_id: int, item_data: Dict[str, Any]):
        await nats_client.publish_item_update(
            item_id, 
            "updated", 
            item_data
        )
    
    @staticmethod
    async def publish_item_deleted(item_id: int):
        await nats_client.publish_item_update(
            item_id, 
            "deleted", 
            {}
        )
    
    @staticmethod
    async def publish_weather_data(weather_data: Dict[str, Any]):
        await nats_client.publish_weather_update(weather_data)