from sqlalchemy.orm import declarative_base

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

Base = declarative_base()

class WeatherItem(Base):
    __tablename__ = "weather_items"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class WeatherHistory(Base):
    __tablename__ = "weather_history"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }