"""Test analysis workflow"""
import subprocess
import time
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_analysis_records(scan_id):
    """Check if analysis records exist for the scan."""
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import select, func
    from app.models.analysis import Analysis
    from app.models.viral_post import ViralPost
    
    async def check():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.count(ViralPost.id)).where(ViralPost.scan_id == scan_id)
            )
            viral_count = result.scalar() or 0
            
            result = await db.execute(
                select(func.count(Analysis.id)).join(ViralPost).where(ViralPost.scan_id == scan_id)
            )
            analysis_count = result.scalar() or 0
            
            return viral_count, analysis_count
    
    viral_count, analysis_count = asyncio.run(check())
    return viral_count, analysis_count

print("Analysis Workflow Test")
print("=" * 60)

# Trigger scan via curl
print("\n[1] Triggering new scan...")
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "http://localhost:8000/api/scans",
    "-H", "Content-Type: application/json",
    "-d", '{"scan_type":"trending","time_range":"24h"}'
], capture_output=True, text=True)

try:
    scan_data = json.loads(result.stdout)
    scan_id = scan_data.get('id')
    print(f"OK - Scan created: ID={scan_id}")
except:
    print(f"ERROR - Failed to create scan: {result.stdout}")
    sys.exit(1)

# Wait for completion
print("\n[2] Waiting for scan and analysis to complete...")
for i in range(30):
    time.sleep(2)
    viral_count, analysis_count = check_analysis_records(scan_id)
    print(f"  Check {i+1}: viral_posts={viral_count}, analysis_records={analysis_count}")
    if viral_count > 0 and analysis_count > 0:
        print("OK - Analysis records created!")
        break

print("\nTest complete!")
