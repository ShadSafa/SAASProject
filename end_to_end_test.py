#!/usr/bin/env python3
"""
Complete end-to-end test of the analysis workflow.
Tests: scan creation -> viral posts -> Celery dispatch -> analysis records -> API retrieval
"""
import asyncio
import sys
import time
import json
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import AsyncSessionLocal
from sqlalchemy import select, func, desc
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.models.user import User


async def create_test_user():
    """Ensure test user exists."""
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
    """Create a scan and return its ID."""
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
    """Execute scan and analysis (simulating what the route does)."""
    from app.tasks.scan_jobs import _run_scan
    from app.tasks.analysis_jobs import analyze_posts_batch

    print(f"\n[SCAN] Running scan {scan_id}...")

    # Run the scan
    viral_post_ids = await _run_scan(scan_id)
    print(f"[OK] Scan complete: {len(viral_post_ids)} posts created")

    # Dispatch analysis task
    if viral_post_ids:
        print(f"[CELERY] Dispatching analysis task to Celery...")
        analyze_posts_batch.delay(scan_id, viral_post_ids)
        print(f"[OK] Task queued for {len(viral_post_ids)} posts")

    return viral_post_ids


async def wait_for_analysis(scan_id, max_wait=60):
    """Poll until analysis records are created."""
    print(f"\n[WAIT] Waiting for Celery to process analysis (max {max_wait}s)...")

    start = time.time()
    while time.time() - start < max_wait:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            count = result.scalar() or 0
            if count > 0:
                print(f"[OK] Analysis complete: {count} records created")
                return True

            elapsed = int(time.time() - start)
            print(f"[POLLING] [{elapsed}s] Checking... (0 records found)")
            time.sleep(2)

    print(f"[ERROR] Timeout: No analysis records created after {max_wait}s")
    return False


async def verify_analysis_data(scan_id):
    """Verify analysis data is complete and correct."""
    print(f"\n[VERIFY] Checking analysis data...")

    async with AsyncSessionLocal() as db:
        # Get all analyses for this scan
        result = await db.execute(
            select(Analysis).join(ViralPost).where(ViralPost.scan_id == scan_id)
        )
        analyses = result.scalars().all()

        if not analyses:
            print("[ERROR] No analysis records found")
            return False

        print(f"[OK] Found {len(analyses)} analysis records:")
        for analysis in analyses:
            summary = analysis.why_viral_summary[:60] if analysis.why_viral_summary else "NO SUMMARY"
            print(f"  Post {analysis.viral_post_id}:")
            print(f"    Summary: {summary}...")
            print(f"    Hook Strength: {analysis.hook_strength_score}")
            print(f"    Emotional Trigger: {analysis.emotional_trigger}")
            print(f"    Engagement Velocity: {analysis.engagement_velocity_score}")

            # Verify required fields
            if not analysis.why_viral_summary:
                print(f"    [ERROR] Missing why_viral_summary")
                return False
            if analysis.hook_strength_score is None:
                print(f"    [ERROR] Missing hook_strength_score")
                return False

        print(f"[OK] All {len(analyses)} records have required data")
        return True


async def test_api_endpoint(scan_id):
    """Simulate what the API endpoint does."""
    print(f"\n[API] Testing API endpoint simulation...")

    async with AsyncSessionLocal() as db:
        # Get first viral post
        result = await db.execute(
            select(ViralPost).where(ViralPost.scan_id == scan_id).limit(1)
        )
        viral_post = result.scalar_one_or_none()

        if not viral_post:
            print("[ERROR] No viral posts found")
            return False

        # Get analysis
        result = await db.execute(
            select(Analysis).where(Analysis.viral_post_id == viral_post.id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            print(f"[ERROR] No analysis found for viral_post {viral_post.id}")
            return False

        # Simulate API response
        response = {
            "id": analysis.id,
            "viral_post_id": analysis.viral_post_id,
            "why_viral_summary": analysis.why_viral_summary,
            "posting_time_score": analysis.posting_time_score,
            "hook_strength_score": analysis.hook_strength_score,
            "engagement_velocity_score": analysis.engagement_velocity_score,
            "save_share_ratio_score": analysis.save_share_ratio_score,
            "hashtag_performance_score": analysis.hashtag_performance_score,
            "audience_retention_score": analysis.audience_retention_score,
            "emotional_trigger": analysis.emotional_trigger,
            "confidence_score": analysis.confidence_score,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        }

        print(f"[OK] API would return for viral_post {viral_post.id}:")
        print(f"     {json.dumps(response, indent=6, default=str)}")
        return True


async def main():
    print("=" * 70)
    print("END-TO-END ANALYSIS WORKFLOW TEST")
    print("=" * 70)

    try:
        # Step 1: Create user
        print("\n[1/5] Creating test user...")
        user_id = await create_test_user()
        print(f"[OK] User ID: {user_id}")

        # Step 2: Create scan
        print("\n[2/5] Creating scan...")
        scan_id = await create_test_scan(user_id)
        print(f"[OK] Scan ID: {scan_id}")

        # Step 3: Run scan and dispatch analysis
        print("\n[3/5] Running scan and dispatching analysis...")
        viral_post_ids = await run_scan_analysis(scan_id)

        # Step 4: Wait for Celery to process
        print("\n[4/5] Waiting for Celery worker to process analysis...")
        if not await wait_for_analysis(scan_id, max_wait=60):
            print("\n[CRITICAL] Analysis task not processed by Celery worker")
            print("Make sure Celery worker is running:")
            print("  cd backend && python -m celery -A app.celery_app worker --loglevel=info")
            return False

        # Step 5: Verify and test API
        print("\n[5/5] Verifying analysis data and testing API endpoint...")
        if not await verify_analysis_data(scan_id):
            return False

        if not await test_api_endpoint(scan_id):
            return False

        print("\n" + "=" * 70)
        print("SUCCESS: Analysis workflow is fully functional!")
        print("=" * 70)
        print("\nWhat this means:")
        print("  1. Scans create viral posts [OK]")
        print("  2. Analysis tasks are dispatched to Celery [OK]")
        print("  3. Celery worker processes the tasks [OK]")
        print("  4. Analysis records are created in database [OK]")
        print("  5. API endpoint can retrieve the data [OK]")
        print("\nNext: Try triggering a scan from the UI and clicking on posts")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n[EXCEPTION] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
