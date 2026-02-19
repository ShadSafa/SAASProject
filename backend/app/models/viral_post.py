from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ViralPost(Base):
    """Viral Instagram post discovered during a scan."""

    __tablename__ = "viral_posts"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    instagram_post_id = Column(String, nullable=False)  # Not unique: same post can appear in multiple scans
    instagram_url = Column(String)
    post_type = Column(String)  # Reel, Carousel, Photo, Video
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON array string
    thumbnail_url = Column(String, nullable=True)       # Original Instagram URL (expires ~1hr)
    thumbnail_s3_url = Column(String, nullable=True)    # S3-cached URL (persistent)
    creator_username = Column(String)
    creator_follower_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    saves_count = Column(BigInteger, default=0)
    shares_count = Column(BigInteger, default=0)
    post_age_hours = Column(Float, nullable=True)
    viral_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="viral_posts")
    analysis = relationship("Analysis", back_populates="viral_post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ViralPost(id={self.id}, post_id={self.instagram_post_id}, score={self.viral_score})>"
