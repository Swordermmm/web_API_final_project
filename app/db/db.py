from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await create_tables_directly()

async def create_tables_directly():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                wind_speed REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                wind_speed REAL,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_weather_items_location 
            ON weather_items(location)
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_weather_history_location 
            ON weather_history(location)
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_weather_history_recorded 
            ON weather_history(recorded_at)
        """))