from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB
    DATABASE_URL: str = "sqlite+aiosqlite:///./weather.db"
    
    # NATS
    NATS_URL: str = "nats://localhost:4222"
    NATS_TOPIC_ITEMS: str = "items.updates"
    NATS_TOPIC_WEATHER: str = "weather.updates"
    
    # Open-Meteo API
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    LATITUDE: float = 55.7558  # Москва
    LONGITUDE: float = 37.6173
    
    # Фоновая задача
    BACKGROUND_TASK_INTERVAL: int = 300  # seconds
    
    class Config:
        env_file = ".env"


settings = Settings()