"""
Trigger a scan and verify analysis workflow directly.
This bypasses the API authentication by using the database and Celery directly.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def trigger_scan_directly():
    """Trigger a scan by creating it in the database and calling the Celery task."""
    from app.database import AsyncSessionLocal
    from app.models.scan import Scan
    from app.models.user import User
    from datetime import datetime
    from app.tasks.scan_jobs import execute_scan
    
    async with AsyncSessionLocal() as db:
        # Get or create a test user
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating test user...")
            user = User(
                email="test@example.com",
                hashed_password="dummy",
                email_verified=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        print(f"Using user: {user.email}")
        
        # Create a scan
        print("Creating scan...")
        scan = Scan(
            user_id=user.id,
            scan_type="trending",
            time_range="24h",
            status="pending"
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        print(f"Scan created: ID={scan.id}")
        
        # Trigger the Celery task (this will queue it)
        print("Triggering analysis task...")
        execute_scan.delay(scan.id)
        
        return scan.id

async def check_results(scan_id):
    """Poll for results."""
    from app.database import AsyncSessionLocal
    from app.models.scan import Scan
    from app.models.viral_post import ViralPost
    from app.models.analysis import Analysis
    from sqlalchemy import select, func
    
    print(f"\nWaiting for scan {scan_id} to complete...")
    
    for attempt in range(60):  # Wait up to 2 minutes
        await asyncio.sleep(2)
        
        async with AsyncSessionLocal() as db:
            # Get scan status
            scan = await db.get(Scan, scan_id)
            viral_count_result = await db.execute(
                select(func.count(ViralPost.id)).where(ViralPost.scan_id == scan_id)
            )
            viral_count = viral_count_result.scalar() or 0
            
            analysis_count_result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            analysis_count = analysis_count_result.scalar() or 0
            
            print(f"  [{attempt+1}] Scan status: {scan.status} | Posts: {viral_count} | Analysis: {analysis_count}")
            
            if viral_count > 0 and analysis_count > 0:
                print(f"\nSUCCESS! Analysis records created!")
                print(f"  Viral posts: {viral_count}")
                print(f"  Analysis records: {analysis_count}")
                return True
    
    print("\nTIMEOUT: Analysis didn't complete in time")
    return False

async def main():
    print("=" * 60)
    print("Direct Scan & Analysis Trigger")
    print("=" * 60)
    
    try:
        scan_id = await trigger_scan_directly()
        await check_results(scan_id)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
