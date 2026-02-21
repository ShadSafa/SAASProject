from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    """AI-powered analysis of why a viral post went viral."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    viral_post_id = Column(Integer, ForeignKey("viral_posts.id", ondelete="CASCADE"), unique=True, nullable=False)

    # AI-generated summary
    why_viral_summary = Column(Text, nullable=True)

    # Algorithm factors (0-100 scores)
    posting_time_score = Column(Float, nullable=True)
    hook_strength_score = Column(Float, nullable=True)
    engagement_velocity_score = Column(Float, nullable=True)
    save_share_ratio_score = Column(Float, nullable=True)
    hashtag_performance_score = Column(JSON, nullable=True)
    audience_retention_score = Column(Float, nullable=True)

    # Qualitative factors
    emotional_trigger = Column(String, nullable=True)  # joy|awe|anger|surprise|sadness|fear

    # AI confidence
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0

    # Phase 5 fields (placeholders for now)
    audience_demographics = Column(JSON, nullable=True)
    content_category = Column(String, nullable=True)
    niche = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    viral_post = relationship("ViralPost", back_populates="analysis")

    def __repr__(self):
        return f"<Analysis(id={self.id}, viral_post_id={self.viral_post_id})>"
