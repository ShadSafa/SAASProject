#!/usr/bin/env python3
"""Time how long analysis takes to complete after dispatch."""
import asyncio
import sys
import time
from pathlib import Path

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.models.user import User

async def main():
    # Create user and scan
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="test@example.com", hashed_password="dummy", email_verified=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        user_id = user.id

    async with AsyncSessionLocal() as db:
        scan = Scan(
            user_id=user_id,
            scan_type="trending",
            time_range="24h",
            status="pending"
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        scan_id = scan.id

    # Run scan
    from app.tasks.scan_jobs import _run_scan
    viral_post_ids = await _run_scan(scan_id)
    print(f"[SCAN] Created {len(viral_post_ids)} posts")

    # Dispatch analysis
    from app.tasks.analysis_jobs import analyze_posts_batch
    loop = asyncio.get_event_loop()

    print(f"[DISPATCH] Dispatching analysis task...")
    dispatch_time = time.time()
    await loop.run_in_executor(None, lambda: analyze_posts_batch.delay(scan_id, viral_post_ids))
    dispatch_end = time.time()
    print(f"[DISPATCH] Task dispatch took {dispatch_end - dispatch_time:.4f}s")

    # Check for analysis records at different intervals
    print(f"\n[POLLING] Checking for analysis records...")
    for i in range(20):
        await asyncio.sleep(0.5)
        elapsed = i * 0.5

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            count = result.scalar() or 0

        if count > 0:
            print(f"[{elapsed:.1f}s] FOUND {count} analysis records!")
            break
        elif i % 2 == 0:
            print(f"[{elapsed:.1f}s] Still waiting ({count} records found)")

asyncio.run(main())
