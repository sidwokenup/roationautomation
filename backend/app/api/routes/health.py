from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
import redis.asyncio as redis
import httpx

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "ok"}

@router.get("/database")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "service": "database"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")

@router.get("/redis")
async def health_check_redis():
    if settings.DEV_MODE:
        return {"status": "ok", "service": "redis", "message": "Disabled in DEV_MODE"}
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        return {"status": "ok", "service": "redis"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Redis connection failed")

@router.get("/palladium")
async def health_check_palladium():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.palladium.expert", timeout=5.0)
            if resp.status_code < 500:
                return {"status": "ok", "service": "palladium"}
            raise Exception("Bad status code")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Palladium API connection failed")
