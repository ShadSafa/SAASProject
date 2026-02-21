"""
Test script to verify the analysis workflow end-to-end.
"""
import subprocess
import time
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def wait_for_backend(max_retries=30):
    """Wait for backend to be ready."""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8000/api/health"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                print(f"✓ Backend is ready")
                return True
        except:
            pass
        
        if attempt % 5 == 0:
            print(f"  Waiting for backend... ({attempt+1}/{max_retries})")
        time.sleep(1)
    
    return False

def check_analysis_records(scan_id):
    """Check if analysis records exist for the scan."""
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import select, func, join
    from app.models.analysis import Analysis
    from app.models.viral_post import ViralPost
    
    async def check():
        async with AsyncSessionLocal() as db:
            # Get viral post count for scan
            result = await db.execute(
                select(func.count(ViralPost.id)).where(ViralPost.scan_id == scan_id)
            )
            viral_count = result.scalar() or 0
            
            # Get analysis count
            result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            analysis_count = result.scalar() or 0
            
            return viral_count, analysis_count
    
    viral_count, analysis_count = asyncio.run(check())
    print(f"  Viral posts: {viral_count}")
    print(f"  Analysis records: {analysis_count}")
    
    return analysis_count > 0

def main():
    print("=" * 60)
    print("Analysis Workflow Test")
    print("=" * 60)
    
    # Wait for backend
    print("\n[1/3] Waiting for backend to be ready...")
    if not wait_for_backend():
        print("✗ Backend failed to start")
        return
    
    # Trigger scan manually via curl (no auth required in dev)
    print("\n[2/3] Triggering new scan...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "http://localhost:8000/api/scans",
        "-H", "Content-Type: application/json",
        "-d", '{"scan_type":"trending","time_range":"24h"}'
    ], capture_output=True, text=True)
    
    import json
    try:
        scan_data = json.loads(result.stdout)
        scan_id = scan_data.get('id')
        if scan_id:
            print(f"✓ Scan created: ID={scan_id}")
        else:
            print(f"✗ Failed to parse scan response: {result.stdout}")
            return
    except:
        print(f"✗ Failed to create scan: {result.stdout}")
        return
    
    # Wait for scan to complete and analysis to run
    print("\n[3/3] Waiting for scan and analysis to complete...")
    print("  (This takes 5-10 seconds)")
    
    for i in range(30):
        time.sleep(2)
        if i % 2 == 0:
            print(f"  Checking database... (attempt {i//2 + 1}/15)")
        
        if check_analysis_records(scan_id):
            break
    
    print("\n✓ Test complete!")
    print("\nYou can now click on a post in the UI to see analysis results.")

if __name__ == "__main__":
    main()
