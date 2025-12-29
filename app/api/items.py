from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.db import get_session
from app.models.models import WeatherItem
from app.models.schemas import (
    WeatherBase, 
    WeatherUpdate, 
    WeatherResponse
)
from app.nats.client import NATSService
from app.ws.websocket import manager

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[WeatherResponse])
async def get_items(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(WeatherItem).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{item_id}", response_model=WeatherResponse)
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(WeatherItem).where(WeatherItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.post("/", response_model=WeatherResponse)
async def create_item(
    payload: WeatherBase,
    session: AsyncSession = Depends(get_session)
):
    db_item = WeatherItem(**payload.dict())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    
    await NATSService.publish_item_created(db_item.id, db_item.to_dict())
    await manager.broadcast_item_update("created", db_item.to_dict())
    
    return db_item


@router.patch("/{item_id}", response_model=WeatherResponse)
async def update_item(
    item_id: int,
    item_update: WeatherUpdate,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(WeatherItem).where(WeatherItem.id == item_id)
    result = await session.execute(stmt)
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    await session.commit()
    await session.refresh(db_item)
    
    await NATSService.publish_item_updated(db_item.id, db_item.to_dict())
    await manager.broadcast_item_update("updated", db_item.to_dict())
    
    return db_item


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(WeatherItem).where(WeatherItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await session.delete(item)
    await session.commit()
    
    await NATSService.publish_item_deleted(item_id)
    await manager.broadcast_item_update("deleted", {"id": item_id})
    
    return {"message": "Item deleted successfully"}