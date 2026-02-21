#!/usr/bin/env python3
"""Monitor Redis queue while dispatching a test task."""
import asyncio
import sys
import time
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))

import redis
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.models.user import User

async def create_test_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="test@example.com", hashed_password="dummy", email_verified=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user.id

async def create_test_scan(user_id):
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
        return scan.id

async def run_scan_analysis(scan_id):
    from app.tasks.scan_jobs import _run_scan
    viral_post_ids = await _run_scan(scan_id)
    return viral_post_ids

async def main():
    print("[SETUP] Creating user and scan...")
    user_id = await create_test_user()
    scan_id = await create_test_scan(user_id)
    print(f"[OK] Scan ID: {scan_id}")

    print("[SETUP] Running scan...")
    viral_post_ids = await run_scan_analysis(scan_id)
    print(f"[OK] Created {len(viral_post_ids)} posts: {viral_post_ids}")

    # Now monitor the queue BEFORE dispatch
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)

    print("\n[BEFORE DISPATCH]")
    queue_len = r.llen("celery")
    all_keys = list(r.keys(b"*"))
    print(f"  Celery queue length: {queue_len}")
    print(f"  Total Redis keys: {len(all_keys)}")

    # Dispatch analysis task
    print("\n[DISPATCH] Calling analyze_posts_batch.delay()...")
    from app.tasks.analysis_jobs import analyze_posts_batch
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: analyze_posts_batch.delay(scan_id, viral_post_ids))
    print("[OK] Dispatch returned")

    # Monitor queue AFTER dispatch
    print("\n[MONITORING QUEUE AFTER DISPATCH]")
    for i in range(10):
        await asyncio.sleep(1)
        queue_len = r.llen("celery")
        all_keys = list(r.keys(b"*"))
        print(f"  [{i+1}s] Queue length: {queue_len}, Redis keys: {len(all_keys)}")

        if queue_len > 0:
            print(f"    ✓ Task found in queue!")
            break

    # Check database for analysis records
    print("\n[CHECKING DATABASE]")
    await asyncio.sleep(2)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).join(ViralPost).where(ViralPost.scan_id == scan_id)
        )
        analyses = result.scalars().all()
        print(f"  Analysis records created: {len(analyses)}")

asyncio.run(main())
