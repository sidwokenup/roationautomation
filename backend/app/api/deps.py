from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import AsyncGenerator
import uuid

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import User, UserRole

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    # Bypass authentication completely
    # Return a dummy admin user to satisfy type hints and route logic
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True
    )

def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user