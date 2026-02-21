#!/usr/bin/env python3
"""
Diagnostic script to test Celery task execution.
Run this to verify the Celery worker can actually process tasks.

Usage:
  Terminal 1: cd backend && python -m celery -A app.celery_app worker --loglevel=debug
  Terminal 2: python celery_diagnostic.py
"""
import sys
import time
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.celery_app import celery_app
from celery.result import AsyncResult


def test_celery_connection():
    """Test if Celery can connect to broker."""
    print("=" * 70)
    print("CELERY DIAGNOSTIC TEST")
    print("=" * 70)

    print("\n[1/3] Testing Celery broker connection...")
    try:
        # Try to inspect the Celery app
        from celery.app.control import Inspect

        inspect = Inspect(app=celery_app)
        active_tasks = inspect.active()

        if active_tasks is None:
            print("[WARNING] Cannot connect to Celery broker")
            print("  - Redis may not be running")
            print("  - Check CELERY_BROKER_URL in config: redis://localhost:6379/0")
            return False
        else:
            print("[OK] Connected to Celery broker")
            print(f"    Active workers: {list(active_tasks.keys())}")
            return True

    except Exception as e:
        print(f"[ERROR] Broker connection failed: {e}")
        return False


def test_task_dispatch():
    """Test if we can dispatch a task to Celery."""
    print("\n[2/3] Testing task dispatch to Celery...")

    try:
        # Import a simple test task
        from app.tasks.analysis_jobs import analyze_posts_batch

        # Queue a simple test task (using dummy IDs that won't exist in DB)
        print("  Dispatching test task: analyze_posts_batch(scan_id=999, viral_post_ids=[999])")
        result = analyze_posts_batch.delay(scan_id=999, viral_post_ids=[999])

        print(f"[OK] Task queued successfully")
        print(f"    Task ID: {result.id}")
        print(f"    Task state: {result.state}")

        return result

    except Exception as e:
        print(f"[ERROR] Task dispatch failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def wait_for_task_result(task_result, max_wait=30):
    """Wait for Celery task to complete."""
    print(f"\n[3/3] Waiting for Celery worker to process task ({max_wait}s timeout)...")

    start = time.time()
    while time.time() - start < max_wait:
        try:
            # Check task state
            if task_result.ready():
                print(f"[OK] Task completed!")
                print(f"    Final state: {task_result.state}")
                print(f"    Result: {task_result.result}")
                return True

            # Still waiting
            elapsed = int(time.time() - start)
            print(f"  [{elapsed}s] Task state: {task_result.state}... (waiting)")
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Error checking task: {e}")
            return False

    print(f"[TIMEOUT] Worker did not process task after {max_wait}s")
    print(f"    Current state: {task_result.state}")
    return False


async def main():
    # Test 1: Broker connection
    broker_ok = test_celery_connection()

    if not broker_ok:
        print("\n" + "=" * 70)
        print("DIAGNOSIS: Cannot connect to Celery broker")
        print("=" * 70)
        print("\nFix this first:")
        print("  1. Make sure Redis is running on localhost:6379")
        print("  2. Start Celery worker: cd backend && python -m celery -A app.celery_app worker --loglevel=debug")
        print("  3. Then run this diagnostic again")
        return False

    # Test 2: Task dispatch
    task_result = test_task_dispatch()

    if task_result is None:
        print("\n" + "=" * 70)
        print("DIAGNOSIS: Cannot dispatch task to Celery")
        print("=" * 70)
        print("\nCheck this:")
        print("  1. Is the Celery app configured correctly?")
        print("  2. Can the app import app.tasks.analysis_jobs?")
        print("  3. Check backend/app/celery_app.py has task imports")
        return False

    # Test 3: Wait for processing
    success = wait_for_task_result(task_result, max_wait=30)

    print("\n" + "=" * 70)
    if success:
        print("SUCCESS: Celery worker is functioning correctly!")
        print("=" * 70)
        print("\nNow try running the full end-to-end test:")
        print("  python end_to_end_test.py")
    else:
        print("DIAGNOSIS: Celery worker is NOT processing tasks")
        print("=" * 70)
        print("\nCheck this:")
        print("  1. Celery worker terminal should show:")
        print("     - 'Ready to accept tasks'")
        print("     - Log messages when tasks are received")
        print("  2. If worker started but shows no task logs:")
        print("     - Task may not be registered (check celery_app.py imports)")
        print("     - Worker may be processing but stuck (check for errors)")
        print("  3. Restart everything:")
        print("     - Stop Redis and Celery worker")
        print("     - Kill any Python processes")
        print("     - Restart Redis, then Celery worker, then this test")

    return success


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
