from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.analysis import Analysis
from app.models.viral_post import ViralPost
from app.schemas.analysis import AnalysisResponse
from app.dependencies import get_current_active_user
from sqlalchemy import select

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{viral_post_id}", response_model=AnalysisResponse)
async def get_analysis(
    viral_post_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_active_user)
):
    """Get analysis results for a viral post."""
    # Verify viral post exists and belongs to user's scan
    result = await db.execute(
        select(ViralPost).where(ViralPost.id == viral_post_id).options(joinedload(ViralPost.scan))
    )
    viral_post = result.scalar_one_or_none()

    if not viral_post:
        raise HTTPException(status_code=404, detail="Viral post not found")

    # Verify user owns this post's scan
    if viral_post.scan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch analysis (may not exist yet if still processing)
    result = await db.execute(
        select(Analysis).where(Analysis.viral_post_id == viral_post_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not yet available")

    return analysis
