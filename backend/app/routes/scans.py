import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_active_user
from app.models.scan import Scan
from app.models.viral_post import ViralPost
from app.models.user import User
from app.schemas.scan import (
    ScanRequest,
    AnalyzeUrlRequest,
    ScanTriggerResponse,
    ScanResponse,
    ViralPostResponse,
    EngagementResponse,
    ScanHistoryItem,
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])

# Basic rate limit: free tier = 5 scans per 30 days
FREE_TIER_MONTHLY_LIMIT = 5


async def _check_scan_limit(user: User, db: AsyncSession) -> None:
    """
    Basic scan limit check for Phase 3.
    Free tier: max 5 scans per rolling 30-day window.
    Phase 10 will replace this with proper subscription tier enforcement.
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(Scan.id))
        .where(Scan.user_id == user.id)
        .where(Scan.created_at >= thirty_days_ago)
    )
    scan_count = result.scalar_one()

    if scan_count >= FREE_TIER_MONTHLY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free tier limit reached: {FREE_TIER_MONTHLY_LIMIT} scans per 30 days. Upgrade to continue.",
        )


def _build_post_response(post: ViralPost) -> ViralPostResponse:
    """Convert ViralPost model to ViralPostResponse schema."""
    return ViralPostResponse(
        id=post.id,
        instagram_post_id=post.instagram_post_id,
        instagram_url=post.instagram_url,
        post_type=post.post_type,
        # Prefer S3 URL (persistent) over Instagram URL (expires ~1h)
        thumbnail_url=post.thumbnail_s3_url or post.thumbnail_url,
        creator_username=post.creator_username,
        creator_follower_count=post.creator_follower_count,
        engagement=EngagementResponse(
            likes=post.likes_count or 0,
            comments=post.comments_count or 0,
            saves=post.saves_count or 0,
            shares=post.shares_count or 0,
        ),
        viral_score=post.viral_score,
        post_age_hours=post.post_age_hours,
    )


@router.post("/trigger", response_model=ScanTriggerResponse)
async def trigger_scan(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Trigger a new time-range viral content scan (SCAN-01, SCAN-02, SCAN-03).
    Returns immediately with scan_id; use GET /scans/status/{scan_id} to poll.
    """
    # Development bypass: allow scans without Instagram account in dev mode
    # Production (Phase 4+) will require proper Instagram OAuth connection
    if not current_user.instagram_accounts and settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connect an Instagram account first to run a scan.",
        )

    # Check rate limit (skip in development mode for checkpoint testing)
    if settings.ENVIRONMENT == "production":
        await _check_scan_limit(current_user, db)

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        scan_type="hashtag",
        time_range=request.time_range,
        status="pending",
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    logger.info(f"Scan {scan.id} created. ENVIRONMENT={settings.ENVIRONMENT}")

    # Development mode: execute synchronously (no Redis/Celery required)
    if settings.ENVIRONMENT == "development":
        logger.info(f"Scan {scan.id} executing in development mode")
        from app.tasks.scan_jobs import _run_scan
        from app.tasks.analysis_jobs import analyze_posts_batch
        try:
            logger.info(f"Scan {scan.id} _run_scan starting")
            viral_post_ids = await _run_scan(scan.id)
            logger.info(f"Scan {scan.id} completed synchronously (dev mode), dispatching analysis for {len(viral_post_ids)} posts")

            # Dispatch analysis task after scan completes
            if viral_post_ids:
                analyze_posts_batch.delay(scan.id, viral_post_ids)
                logger.info(f"Scan {scan.id} analysis dispatched for {len(viral_post_ids)} posts")
        except Exception as e:
            logger.error(f"Scan {scan.id} failed: {e}", exc_info=True)
    else:
        # Production: dispatch Celery task (non-blocking)
        logger.info(f"Scan {scan.id} dispatching to Celery")
        from app.tasks.scan_jobs import execute_scan
        execute_scan.delay(scan.id)
        logger.info(f"Scan {scan.id} dispatched for user {current_user.id} (time_range={request.time_range})")

    return ScanTriggerResponse(
        scan_id=scan.id,
        status="pending",
        message=f"Scan started. Discovering viral posts from the last {request.time_range}.",
    )


@router.post("/analyze-url", response_model=ScanTriggerResponse)
async def analyze_url(
    request: AnalyzeUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze a specific Instagram post URL (SCAN-05, SCAN-06).
    Returns immediately with scan_id; poll GET /scans/status/{scan_id} for results.
    """
    # Validate Instagram URL format
    from app.services.scan_service import extract_post_id_from_url
    post_id = extract_post_id_from_url(request.instagram_url)
    if not post_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid Instagram URL. Expected format: https://www.instagram.com/p/SHORTCODE/ or /reel/SHORTCODE/",
        )

    if not current_user.instagram_accounts and settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connect an Instagram account first to analyze posts.",
        )

    # Check rate limit (skip in development mode for checkpoint testing)
    if settings.ENVIRONMENT == "production":
        await _check_scan_limit(current_user, db)

    scan = Scan(
        user_id=current_user.id,
        scan_type="url",
        target_url=request.instagram_url,
        status="pending",
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Development mode: execute synchronously (no Redis/Celery required)
    if settings.ENVIRONMENT == "development":
        from app.tasks.scan_jobs import _run_scan
        from app.tasks.analysis_jobs import analyze_posts_batch
        try:
            viral_post_ids = await _run_scan(scan.id)
            logger.info(f"Scan {scan.id} completed synchronously (dev mode)")

            # Dispatch analysis task after scan completes
            if viral_post_ids:
                analyze_posts_batch.delay(scan.id, viral_post_ids)
                logger.info(f"Scan {scan.id} analysis dispatched for {len(viral_post_ids)} posts")
        except Exception as e:
            logger.error(f"Scan {scan.id} failed: {e}", exc_info=True)
    else:
        # Production: dispatch Celery task (non-blocking)
        from app.tasks.scan_jobs import execute_scan
        execute_scan.delay(scan.id)

    return ScanTriggerResponse(
        scan_id=scan.id,
        status="pending",
        message=f"Analyzing post: {request.instagram_url}",
    )


@router.get("/status/{scan_id}", response_model=ScanResponse)
async def get_scan_status(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get scan status and results (SCAN-07).
    Frontend polls this every 2s until status is 'completed' or 'failed'.
    """
    result = await db.execute(
        select(Scan)
        .where(Scan.id == scan_id)
        .options(selectinload(Scan.viral_posts))
    )
    scan = result.scalar_one_or_none()

    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return ScanResponse(
        scan_id=scan.id,
        status=scan.status,
        scan_type=scan.scan_type,
        time_range=scan.time_range,
        target_url=scan.target_url,
        created_at=scan.created_at,
        completed_at=scan.completed_at,
        error_message=scan.error_message,
        results=[_build_post_response(p) for p in scan.viral_posts],
    )


@router.get("/history", response_model=List[ScanHistoryItem])
async def get_scan_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
):
    """
    List past scans for the current user (most recent first).
    """
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .limit(limit)
        .options(selectinload(Scan.viral_posts))
    )
    scans = result.scalars().all()

    return [
        ScanHistoryItem(
            scan_id=s.id,
            status=s.status,
            scan_type=s.scan_type,
            time_range=s.time_range,
            created_at=s.created_at,
            completed_at=s.completed_at,
            post_count=len(s.viral_posts),
        )
        for s in scans
    ]
