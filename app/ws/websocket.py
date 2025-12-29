import json
import asyncio
import logging
from typing import Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect
from app.models.schemas import WebSocketMessage

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Новый WebSocket подключён. Всего: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket отсоединён. Всего: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Ошибка трансляции сообщения: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_item_update(self, action: str, item_data: Dict[str, Any]):
        message = WebSocketMessage(
            type=f"item_{action}",
            data=item_data
        )
        await self.broadcast(message.dict())

manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"Получено WebSocket сообщение: {message}")
                
                # Echo back (or process as needed)
                await websocket.send_json({
                    "type": "echo",
                    "data": message,
                    "timestamp": asyncio.get_event_loop().time()
                })
            except json.JSONDecodeError:
                logger.warning(f"Получен невалидный JSON: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Ошибка WebSocket: {e}")
        manager.disconnect(websocket)