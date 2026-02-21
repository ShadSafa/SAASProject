#!/usr/bin/env python3
"""Simple test to verify task dispatch works."""
import sys
import asyncio
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))


async def main():
    print("=" * 70)
    print("SIMPLE TASK DISPATCH TEST")
    print("=" * 70)

    try:
        print("\n[1] Importing task...")
        from app.tasks.analysis_jobs import analyze_posts_batch
        print("  ✓ Task imported")

        print("\n[2] Dispatching task...")
        result = analyze_posts_batch.delay(scan_id=999, viral_post_ids=[999])
        print(f"  ✓ Task queued: {result.id}")
        print(f"  State: {result.state}")

        print("\n[3] Task dispatched successfully")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
