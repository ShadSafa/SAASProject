#!/usr/bin/env python3
"""Debug the complete analysis flow step by step."""
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
    print("="*70)
    print("COMPLETE ANALYSIS WORKFLOW DEBUG")
    print("="*70)

    # Step 1: Create user
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="test@example.com", hashed_password="dummy", email_verified=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        user_id = user.id
        print(f"\n[USER] ID: {user_id}, email: {user.email}")

    # Step 2: Create scan
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
        print(f"\n[SCAN] ID: {scan_id} created")

    # Step 3: Run scan synchronously (as the route does in development)
    print(f"\n[RUN_SCAN] Starting scan execution...")
    from app.tasks.scan_jobs import _run_scan

    viral_post_ids = await _run_scan(scan_id)
    print(f"[RUN_SCAN] Completed, got {len(viral_post_ids)} post IDs: {viral_post_ids}")

    # Step 4: Verify posts exist in database
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(ViralPost.id)).where(ViralPost.scan_id == scan_id))
        post_count = result.scalar() or 0
        print(f"\n[VERIFY] Database has {post_count} posts for scan {scan_id}")

        result = await db.execute(select(ViralPost).where(ViralPost.scan_id == scan_id))
        posts = result.scalars().all()
        for post in posts[:3]:
            print(f"  Post {post.id}: {post.creator_username}")

    # Step 5: Dispatch analysis task
    print(f"\n[DISPATCH] Dispatching analysis task...")
    from app.tasks.analysis_jobs import analyze_posts_batch
    loop = asyncio.get_event_loop()

    task = await loop.run_in_executor(None, lambda: analyze_posts_batch.delay(scan_id, viral_post_ids))
    print(f"[DISPATCH] Task dispatched: {task.id if hasattr(task, 'id') else 'unknown'}")

    # Step 6: Wait and check for analysis records
    print(f"\n[WAIT] Waiting for analysis records to be created...")
    for i in range(15):
        await asyncio.sleep(1)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            analysis_count = result.scalar() or 0

        elapsed = (i + 1) * 1
        if analysis_count > 0:
            print(f"[{elapsed}s] FOUND {analysis_count} analysis records!")
            break
        elif i % 3 == 0:
            print(f"[{elapsed}s] Waiting... ({analysis_count} records found)")

    # Step 7: Final check
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).join(ViralPost).where(ViralPost.scan_id == scan_id)
        )
        analyses = result.scalars().all()

        print(f"\n[FINAL] Scan {scan_id}:")
        print(f"  Total viral posts: {len(viral_post_ids)}")
        print(f"  Analysis records created: {len(analyses)}")

        if len(analyses) == 0:
            print(f"\n[ERROR] Analysis records were NOT created!")
            print(f"Check the Celery worker logs for exceptions.")
        else:
            print(f"\n[SUCCESS] Analysis workflow is working!")
            for a in analyses[:2]:
                print(f"  - Post {a.viral_post_id}: {a.why_viral_summary[:40]}...")

asyncio.run(main())
