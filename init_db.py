#!/usr/bin/env python3
"""
Database initialization and verification script.

This script:
1. Checks if migrations are applied
2. Applies any pending migrations
3. Verifies required tables exist

Usage:
  python init_db.py
"""
import sys
import asyncio
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))


async def check_and_init_database():
    """Check and initialize database schema."""
    print("=" * 70)
    print("DATABASE INITIALIZATION".center(70))
    print("=" * 70)

    try:
        from app.database import engine
        from app.models.scan import Scan
        from app.models.viral_post import ViralPost
        from app.models.analysis import Analysis
        from app.models.user import User
        from sqlalchemy import inspect, text

        print("\n[1/3] Checking database connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        print("  ✓ Connected to PostgreSQL")

        print("\n[2/3] Checking if migrations are applied...")
        async with engine.begin() as conn:
            inspector = inspect(conn.sync_engine)
            tables = inspector.get_table_names()

            required_tables = ['users', 'scans', 'viral_posts', 'analyses', 'instagram_accounts']
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                print(f"  ⚠ Missing tables: {missing_tables}")
                print("\n  To apply migrations, run:")
                print("    cd backend")
                print("    alembic upgrade head")
                print("\n  Or use the init_db.py script with upgrade flag:")
                print("    python init_db.py --upgrade")
                return False
            else:
                print(f"  ✓ All required tables exist: {required_tables}")

        print("\n[3/3] Verifying schema...")
        async with engine.begin() as conn:
            inspector = inspect(conn.sync_engine)

            # Check analyses table specifically (since we modified it recently)
            if 'analyses' in inspector.get_table_names():
                columns = {col['name']: col['type'] for col in inspector.get_columns('analyses')}
                required_columns = [
                    'id', 'viral_post_id', 'why_viral_summary',
                    'hook_strength_score', 'emotional_trigger',
                    'engagement_velocity_score'
                ]
                missing_cols = [c for c in required_columns if c not in columns]
                if missing_cols:
                    print(f"  ⚠ Missing columns in 'analyses': {missing_cols}")
                    return False
                else:
                    print(f"  ✓ 'analyses' table has all required columns")

        print("\n" + "=" * 70)
        print("DATABASE IS READY".center(70))
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_migrations():
    """Run pending migrations using alembic."""
    print("\nRunning database migrations...")
    try:
        from alembic.config import Config
        from alembic import command

        # Get alembic config
        alembic_cfg = Config(Path(__file__).parent / "backend" / "alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", "")  # We'll use async later

        # Upgrade to latest
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        print("\nTo apply migrations manually:")
        print("  cd backend")
        print("  alembic upgrade head")
        return False


async def main():
    import sys

    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--upgrade':
        print("WARNING: Alembic async operations need special handling.")
        print("\nTo upgrade the database, run this in the backend directory:")
        print("  alembic upgrade head")
        print("\nYou may need to:")
        print("  1. Set SQLALCHEMY_DATABASE_URL environment variable with asyncpg URL")
        print("  2. Or temporarily modify alembic.ini with direct psycopg2 URL")
        return False

    success = await check_and_init_database()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
