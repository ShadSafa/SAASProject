import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import AsyncSessionLocal
from sqlalchemy import select, update
from app.models.user import User

async def verify_test_user():
    async with AsyncSessionLocal() as db:
        stmt = update(User).where(User.email == "test@example.com").values(email_verified=True)
        await db.execute(stmt)
        await db.commit()
        print("Email verified for test@example.com")

asyncio.run(verify_test_user())
