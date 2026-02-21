#!/usr/bin/env python3
"""Test the analysis endpoint with authentication."""
import asyncio
import sys
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.user import User
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.models.analysis import Analysis
from app.services.security import create_access_token

async def main():
    print("Testing analysis endpoint with authentication\n")
    
    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            print("ERROR: test user not found")
            return
        
        # Get a scan with analysis
        result = await db.execute(
            select(Scan).where(Scan.user_id == user.id)
            .order_by(Scan.id.desc()).limit(1)
        )
        scan = result.scalar_one_or_none()
        if not scan:
            print("ERROR: no scans found")
            return
        
        # Get first post with analysis
        result = await db.execute(
            select(ViralPost, Analysis)
            .outerjoin(Analysis, Analysis.viral_post_id == ViralPost.id)
            .where(ViralPost.scan_id == scan.id)
        )
        row = result.first()
        if not row:
            print("ERROR: no posts found")
            return
        
        post, analysis = row
        if not analysis:
            print(f"ERROR: post {post.id} has no analysis")
            return
        
        # Generate token
        token = create_access_token({"sub": user.email}, expires_delta=None)
        print(f"User: {user.email}")
        print(f"Scan ID: {scan.id}")
        print(f"Post ID: {post.id}")
        print(f"Token: {token[:50]}...\n")
        
        print(f"Test: GET /api/analysis/{post.id}")
        print(f"Auth: Bearer {token[:30]}...\n")
        
        # Show curl command
        print("Curl command:")
        print(f'curl -s "http://127.0.0.1:9000/api/analysis/{post.id}" \')
        print(f'  -H "Authorization: Bearer {token}"')

asyncio.run(main())
