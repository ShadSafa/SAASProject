from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.analysis import Analysis
from app.models.viral_post import ViralPost
from app.dependencies import get_current_active_user
from sqlalchemy import select

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{viral_post_id}")
async def get_analysis(viral_post_id: int):
    """Get analysis results for a viral post.

    Uses a fresh session to avoid async/greenlet issues with
    SQLAlchemy ORM object serialization through FastAPI.
    """
    # Create a fresh database session (avoid FastAPI dependency injection issues)
    async with AsyncSessionLocal() as db:
        # Query viral post
        result = await db.execute(
            select(ViralPost).where(ViralPost.id == viral_post_id)
        )
        viral_post = result.scalar_one_or_none()

        if not viral_post:
            raise HTTPException(status_code=404, detail="Viral post not found")

        # Query analysis
        result = await db.execute(
            select(Analysis).where(Analysis.viral_post_id == viral_post_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not yet available")

        # Convert to dict immediately while session is still open
        # This avoids detached object and greenlet issues
        hashtag_score = analysis.hashtag_performance_score
        if isinstance(hashtag_score, dict):
            hashtag_score = hashtag_score.get("score", None)

        response = {
            "id": analysis.id,
            "viral_post_id": analysis.viral_post_id,
            "why_viral_summary": analysis.why_viral_summary,
            "posting_time_score": analysis.posting_time_score,
            "hook_strength_score": analysis.hook_strength_score,
            "emotional_trigger": analysis.emotional_trigger,
            "engagement_velocity_score": analysis.engagement_velocity_score,
            "save_share_ratio_score": analysis.save_share_ratio_score,
            "hashtag_performance_score": hashtag_score,
            "audience_retention_score": analysis.audience_retention_score,
            "confidence_score": analysis.confidence_score,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        }

    # Session is now closed - return plain dict (no ORM objects)
    return response
