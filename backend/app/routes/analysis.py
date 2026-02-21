from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import select
import logging

from app.database import AsyncSessionLocal
from app.models.analysis import Analysis
from app.models.viral_post import ViralPost
from app.models.user import User
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)


class NicheOverrideRequest(BaseModel):
    niche_override: str | None = None


@router.get("/{viral_post_id}")
async def get_analysis(
    viral_post_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get analysis results for a viral post.

    Uses a fresh session to avoid async/greenlet issues with
    SQLAlchemy ORM object serialization through FastAPI.
    """
    # Create a fresh database session
    async with AsyncSessionLocal() as db:
        # Query analysis directly
        result = await db.execute(
            select(Analysis).where(Analysis.viral_post_id == viral_post_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not yet available")

        # Query viral post to verify it exists
        result = await db.execute(
            select(ViralPost).where(ViralPost.id == viral_post_id)
        )
        viral_post = result.scalar_one_or_none()

        if not viral_post:
            raise HTTPException(status_code=404, detail="Viral post not found")

        # Convert to dict immediately while session is still open
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

    return response


@router.patch("/{analysis_id}/niche-override")
async def patch_analysis_niche_override(
    analysis_id: int = Path(..., gt=0),
    request: NicheOverrideRequest = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Save user niche override for an analysis record.

    Args:
        analysis_id: Analysis record ID
        request: Request body with niche_override field (or None to clear override)

    Returns:
        Updated analysis record with user_niche_override saved

    Raises:
        HTTPException: 404 if analysis not found, 400 if invalid input
    """
    try:
        async with AsyncSessionLocal() as db:
            # Fetch analysis
            result = await db.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()

            if not analysis:
                raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

            # Get niche override from request
            niche_override = request.niche_override if request else None

            # Validate niche override if provided
            if niche_override:
                if len(niche_override.strip()) == 0:
                    raise HTTPException(status_code=400, detail="Niche override cannot be empty")
                if len(niche_override) > 255:
                    raise HTTPException(status_code=400, detail="Niche override too long (max 255 chars)")

            # Save override
            analysis.user_niche_override = niche_override.strip() if niche_override else None
            await db.commit()
            await db.refresh(analysis)

            logger.info(f"Niche override saved for analysis {analysis_id}: {niche_override}")

            return {
                "id": analysis.id,
                "niche": analysis.niche,  # AI-detected niche
                "user_niche_override": analysis.user_niche_override,  # User override
                "effective_niche": analysis.user_niche_override or analysis.niche  # For UI display
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving niche override for analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save niche override")
