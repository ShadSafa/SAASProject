#!/usr/bin/env python3
"""
QUICK FIX: Verify and troubleshoot the analysis workflow.
Runs a series of checks to identify what's broken and how to fix it.

Usage:
  python quick_fix.py

This script will:
1. Check database connection
2. Check Redis connection
3. Verify Celery configuration
4. Try to run a simple test
5. Provide detailed diagnostics if something fails
"""
import sys
import time
import asyncio
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))


def print_header(text):
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)


def print_step(num, text):
    print(f"\n[STEP {num}] {text}")
    print("-" * 70)


def print_ok(text):
    print(f"  ✓ {text}")


def print_error(text):
    print(f"  ✗ {text}")


def print_warning(text):
    print(f"  ⚠ {text}")


async def check_database():
    """Verify PostgreSQL connection."""
    print_step(1, "Checking PostgreSQL connection...")

    try:
        from app.database import engine
        from app.models.user import User
        from sqlalchemy import select

        # Try to connect and run a query
        async with engine.begin() as conn:
            result = await conn.execute(select(1))
            result.scalar()
        print_ok("PostgreSQL is running and accessible")
        return True
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {e}")
        print_warning("Make sure PostgreSQL is running with database: instagram_analyzer")
        print_warning(f"Check .env file: DATABASE_URL=postgresql+asyncpg://...")
        return False


async def check_redis():
    """Verify Redis connection."""
    print_step(2, "Checking Redis connection...")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print_ok("Redis is running on localhost:6379")
        return True
    except ImportError:
        print_warning("redis module not installed (this might be OK for now)")
        return None
    except Exception as e:
        print_error(f"Redis connection failed: {e}")
        print_warning("Redis is not running or not accessible")
        print("  To start Redis:")
        print("    - Windows: redis-server.exe (if downloaded)")
        print("    - WSL: redis-server")
        print("    - Docker: docker run -d -p 6379:6379 redis:7")
        return False


async def check_celery():
    """Verify Celery can connect to broker."""
    print_step(3, "Checking Celery broker connection...")

    try:
        from app.celery_app import celery_app
        from celery.app.control import Inspect

        inspect = Inspect(app=celery_app)
        active_tasks = inspect.active()

        if active_tasks is None:
            print_error("Cannot connect to Celery broker")
            print_warning("This usually means Redis is not running")
            return False
        else:
            workers = list(active_tasks.keys())
            if workers:
                print_ok(f"Connected to Celery broker with {len(workers)} worker(s) running")
                for worker in workers:
                    print_ok(f"  - {worker}")
                return True
            else:
                print_warning("Connected to Celery broker but NO WORKERS found")
                print_warning("You need to start a Celery worker:")
                print("  cd backend && python -m celery -A app.celery_app worker --loglevel=debug")
                return None

    except Exception as e:
        print_error(f"Celery check failed: {e}")
        print_warning("Make sure Redis is running first")
        return False


async def check_tasks_registered():
    """Verify Celery tasks are registered."""
    print_step(4, "Checking if Celery tasks are registered...")

    try:
        from app.celery_app import celery_app

        tasks = celery_app.tasks
        required_tasks = [
            "analysis.analyze_posts_batch",
            "scan.execute_scan",
        ]

        registered = []
        missing = []

        for task_name in required_tasks:
            if task_name in tasks:
                registered.append(task_name)
            else:
                missing.append(task_name)

        if registered:
            for task in registered:
                print_ok(f"Task registered: {task}")

        if missing:
            for task in missing:
                print_error(f"Task NOT registered: {task}")
            print_warning("Check backend/app/celery_app.py has task imports")
            return False

        return True

    except Exception as e:
        print_error(f"Task registration check failed: {e}")
        return False


async def check_analysis_model():
    """Verify Analysis model and database schema."""
    print_step(5, "Checking Analysis model and schema...")

    try:
        from app.models.analysis import Analysis
        from app.database import engine
        from sqlalchemy import inspect

        # Check if analyses table exists
        async with engine.connect() as conn:
            inspector = inspect(conn.sync_engine)
            tables = inspector.get_table_names()

            if "analyses" not in tables:
                print_error("Table 'analyses' does not exist in database")
                print_warning("Run database migrations to create tables")
                return False

            columns = {col['name']: col['type'] for col in inspector.get_columns('analyses')}
            required_columns = [
                'id', 'viral_post_id', 'why_viral_summary', 'hook_strength_score',
                'emotional_trigger', 'engagement_velocity_score'
            ]

            missing = [col for col in required_columns if col not in columns]

            if missing:
                print_error(f"Missing columns in 'analyses' table: {missing}")
                return False

            print_ok("Analysis table schema is correct")
            return True

    except Exception as e:
        print_error(f"Model check failed: {e}")
        return False


async def test_simple_task():
    """Test dispatching and processing a simple Celery task."""
    print_step(6, "Testing simple Celery task execution...")

    try:
        from app.tasks.analysis_jobs import analyze_posts_batch

        print("  Dispatching test task to Celery...")
        result = analyze_posts_batch.delay(scan_id=9999, viral_post_ids=[9999])

        print(f"  Task ID: {result.id}")
        print(f"  Initial state: {result.state}")

        # Wait a bit for processing
        for i in range(10):
            time.sleep(0.5)
            if result.ready():
                if result.successful():
                    print_ok(f"Task completed successfully! Result: {result.result}")
                    return True
                else:
                    print_warning(f"Task failed with: {result.result}")
                    return None
            else:
                print(f"    [{i+1}] State: {result.state}...")

        print_warning("Task did not complete within 5 seconds")
        print_warning("Celery worker may not be running")
        return None

    except Exception as e:
        print_error(f"Task test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print_header("CELERY ANALYSIS WORKFLOW - QUICK FIX")

    checks = {
        "PostgreSQL": await check_database(),
        "Redis": await check_redis(),
        "Celery Broker": await check_celery(),
        "Tasks Registered": await check_tasks_registered(),
        "Analysis Schema": await check_analysis_model(),
    }

    # Only try task test if basic checks pass
    if checks.get("Celery Broker") and checks.get("Tasks Registered"):
        checks["Task Execution"] = await test_simple_task()

    # Summary
    print_header("DIAGNOSTIC SUMMARY")

    passed = sum(1 for v in checks.values() if v is True)
    failed = sum(1 for v in checks.values() if v is False)
    warnings = sum(1 for v in checks.values() if v is None)

    for check_name, result in checks.items():
        if result is True:
            print_ok(f"{check_name}")
        elif result is False:
            print_error(f"{check_name}")
        else:
            print_warning(f"{check_name}")

    print()
    print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")

    # Recommendations
    print_header("NEXT STEPS")

    if checks.get("PostgreSQL") is False:
        print("\n1. Fix PostgreSQL:")
        print("   - Make sure PostgreSQL is running")
        print("   - Check database 'instagram_analyzer' exists")
        print("   - Check credentials in .env: DATABASE_URL")

    if checks.get("Redis") is False:
        print("\n2. Start Redis (required for Celery):")
        print("   - Windows with WSL: wsl redis-server")
        print("   - Docker: docker run -d -p 6379:6379 redis:7")
        print("   - Download: https://github.com/microsoftarchive/redis/releases")

    if checks.get("Celery Broker") is None:
        print("\n3. Start Celery Worker:")
        print("   cd backend")
        print("   python -m celery -A app.celery_app worker --loglevel=debug")
        print("   (Watch for 'Ready to accept tasks' message)")

    if all(checks.values()):
        print("\n✓ All checks passed!")
        print("\nYou can now:")
        print("  1. Run: python end_to_end_test.py")
        print("  2. Or start the backend API and test in the UI")
    elif failed == 0 and warnings > 0:
        print("\n✓ Most checks passed, but some components need attention")
        print("Follow the steps above to resolve warnings")
    else:
        print("\n✗ Some critical checks failed")
        print("Fix the issues above before testing the workflow")

    print("\n" + "=" * 70)

    return all(v is not False for v in checks.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
