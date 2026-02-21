#!/usr/bin/env python3
"""Test imports."""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("Testing imports...")

try:
    print("1. Importing celery_app...")
    from app.celery_app import celery_app
    print("   OK")

    print("2. Importing task module...")
    from app.tasks import analysis_jobs
    print("   OK")

    print("3. Getting task...")
    task = celery_app.tasks.get('analysis.analyze_posts_batch')
    print(f"   OK - Task: {task}")

    print("\n✓ All imports successful")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
