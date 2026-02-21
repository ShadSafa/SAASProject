#!/usr/bin/env python3
"""Test the analyze_posts_batch task directly."""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def main():
    print("Testing analyze_posts_batch task...")

    try:
        from app.database import AsyncSessionLocal
        from app.models.viral_post import ViralPost
        from app.models.analysis import Analysis

        # Create a test viral post first
        print("\n1. Creating test viral post...")
        async with AsyncSessionLocal() as db:
            test_post = ViralPost(
                scan_id=999,
                instagram_post_id="test_post_123",
                instagram_url="https://instagram.com/p/test/",
                post_type="Photo",
                caption="Test post for analysis",
                hashtags='["test"]',
                thumbnail_url="https://via.placeholder.com/400",
                creator_username="testuser",
                creator_follower_count=1000,
                likes_count=100,
                comments_count=10,
                saves_count=50,
                shares_count=5,
                post_age_hours=1.0,
                viral_score=50.0
            )
            db.add(test_post)
            await db.commit()
            await db.refresh(test_post)
            post_id = test_post.id
            print(f"   Created viral post ID: {post_id}")

        # Now test the analyze_posts_batch function directly (not via Celery)
        print("\n2. Testing _run_analysis function directly...")
        from app.tasks.analysis_jobs import _run_analysis

        result = await _run_analysis(scan_id=999, viral_post_ids=[post_id])
        print(f"   Analysis result: {result}")

        # Check if analysis record was created
        print("\n3. Checking if analysis record was created...")
        async with AsyncSessionLocal() as db:
            analysis = await db.get(Analysis, post_id)
            if analysis:
                print(f"   SUCCESS: Analysis found!")
                print(f"   - ID: {analysis.id}")
                print(f"   - Summary: {analysis.why_viral_summary[:60]}...")
                print(f"   - Hook Strength: {analysis.hook_strength_score}")
            else:
                print(f"   ERROR: No analysis record found for viral_post_id={post_id}")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
