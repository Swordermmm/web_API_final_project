from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import items, tasks, weather
from app.ws.websocket import websocket_endpoint
from app.db.db import init_db
from app.nats.client import nats_client
from app.tasks.task import background_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    
    await init_db()
    logger.info("Database инициализирован")
    
    await nats_client.connect()
    logger.info("NATS client инициализирован")
    
    await background_task.start()
    logger.info("Фоновая загрузка запушена")
    
    yield
    
    logger.info("Отключение...")
    
    await background_task.stop()
    
    await nats_client.disconnect()


app = FastAPI(
    title="Weather Parser API",
    description="Weather Parser with FastAPI",
    version="0.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(tasks.router)
app.include_router(weather.router)

app.add_api_websocket_route("/ws/items", websocket_endpoint)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )