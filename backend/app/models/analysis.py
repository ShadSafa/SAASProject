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

    # Phase 5 fields: Audience insights
    audience_demographics = Column(JSON, nullable=True)
    # Structure: {
    #   "age_range": {"13-17": 5, "18-24": 25, "25-34": 45, "35-44": 20, "45+": 5},
    #   "gender_distribution": {"male": 40, "female": 55, "other": 5},
    #   "top_countries": [
    #     {"code": "US", "percentage": 45},
    #     {"code": "GB", "percentage": 12},
    #     {"code": "CA", "percentage": 8}
    #   ]
    # }

    engagement_rate = Column(Float, nullable=True)  # Percentage (0-100)
    # Calculation: (likes + comments + saves + shares) / follower_count * 100

    audience_interests = Column(JSON, nullable=True)
    # Structure: {
    #   "inferred_topics": ["fitness", "nutrition", "wellness"],
    #   "content_affinity": ["educational", "inspirational", "lifestyle"],
    #   "hashtag_analysis": ["#fitnessmotivation", "#healthylifestyle"]
    # }

    content_category = Column(String, nullable=True)
    niche = Column(String, nullable=True)

    # Phase 05-08: User niche override
    user_niche_override = Column(String, nullable=True)
    # When user provides override, store here. Overrides AI-detected niche field for display.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    viral_post = relationship("ViralPost", back_populates="analysis")

    def __repr__(self):
        return f"<Analysis(id={self.id}, viral_post_id={self.viral_post_id})>"
