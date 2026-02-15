from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    """AI-powered analysis of why a viral post went viral."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    viral_post_id = Column(Integer, ForeignKey("viral_posts.id", ondelete="CASCADE"), unique=True, nullable=False)
    why_viral_summary = Column(Text)
    hook_strength = Column(String)
    emotional_trigger = Column(String)
    posting_time_score = Column(Float)
    engagement_velocity = Column(Float)
    save_share_ratio = Column(Float)
    hashtag_performance = Column(JSON)
    audience_demographics = Column(JSON)
    content_category = Column(String)
    niche = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    viral_post = relationship("ViralPost", back_populates="analysis")

    def __repr__(self):
        return f"<Analysis(id={self.id}, viral_post_id={self.viral_post_id})>"
