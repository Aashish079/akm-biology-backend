import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings

async def create_admin():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        email = settings.admin_email
        password = settings.admin_password
        
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalars().first()
        if existing:
            print("Admin user already exists")
            return
    
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
            full_name="Super Admin"
        )
        db.add(admin)
        await db.commit()
        print(f"Admin created. Email: {email}, Password: {password}")

if __name__ == "__main__":
    asyncio.run(create_admin())
