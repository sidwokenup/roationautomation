import asyncio
from app.db.session import AsyncSessionLocal, engine, Base
from app.db.models import User, UserRole
from app.core.security import get_password_hash

async def create_admin():
    # Force table creation first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        await db.commit()
        print("Admin user created: admin@example.com / Password123!")

if __name__ == "__main__":
    asyncio.run(create_admin())
