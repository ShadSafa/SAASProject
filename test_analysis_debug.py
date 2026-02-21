#!/usr/bin/env python3
"""Debug the analysis task step by step."""
import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import AsyncSessionLocal
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.services.openai_service import analyze_viral_post
from app.services.cache_service import get_cached_analysis

async def test_run_analysis():
    """Test the _run_analysis function."""
    scan_id = 61
    viral_post_ids = [102, 103]

    print(f'\n[TEST] Running analysis for scan {scan_id}, posts {viral_post_ids}')

    analyzed_count = 0
    cached_count = 0
    failed_count = 0

    async with AsyncSessionLocal() as db:
        for post_id in viral_post_ids:
            try:
                print(f'\n[POST {post_id}] Starting...')

                # Check cache
                cached_result = get_cached_analysis(post_id)
                cache_status = "HIT" if cached_result else "MISS"
                print(f'  Cache check: {cache_status}')

                if cached_result:
                    print(f'  Using cached result')
                    cached_count += 1
                    continue

                # Fetch viral post
                viral_post = await db.get(ViralPost, post_id)
                if not viral_post:
                    print(f'  ERROR: Post not found')
                    failed_count += 1
                    continue

                print(f'  Found post: {viral_post.creator_username}')

                # Analyze
                print(f'  Calling analyze_viral_post...')
                openai_result = analyze_viral_post(viral_post)
                print(f'  Analysis complete: {openai_result.why_viral_summary[:40]}...')

                # Create Analysis record
                print(f'  Creating Analysis record...')
                analysis = Analysis(
                    viral_post_id=post_id,
                    why_viral_summary=openai_result.why_viral_summary,
                    hook_strength_score=openai_result.hook_strength,
                    emotional_trigger=openai_result.emotional_trigger,
                    posting_time_score=openai_result.posting_time_score,
                    engagement_velocity_score=openai_result.engagement_velocity_score,
                    save_share_ratio_score=openai_result.save_share_ratio_score,
                    hashtag_performance_score=openai_result.hashtag_performance,
                    audience_retention_score=openai_result.audience_retention,
                )
                db.add(analysis)
                await db.flush()
                print(f'  Flush complete')

                analyzed_count += 1

            except Exception as exc:
                print(f'  ERROR: {exc}')
                import traceback
                traceback.print_exc()
                failed_count += 1

        # Commit
        print(f'\n[COMMIT] Committing all changes...')
        await db.commit()
        print(f'[DONE] Analyzed={analyzed_count}, Cached={cached_count}, Failed={failed_count}')

asyncio.run(test_run_analysis())
