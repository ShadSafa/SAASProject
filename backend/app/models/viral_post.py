from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ViralPost(Base):
    """Viral Instagram post discovered during a scan."""

    __tablename__ = "viral_posts"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    instagram_post_id = Column(String, unique=True, nullable=False)
    instagram_url = Column(String)
    post_type = Column(String)  # Reel, Carousel, Photo, Video
    thumbnail_url = Column(String)
    creator_username = Column(String)
    creator_follower_count = Column(Integer)
    likes_count = Column(Integer)
    comments_count = Column(Integer)
    saves_count = Column(Integer)
    shares_count = Column(Integer)
    viral_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scan = relationship("Scan", back_populates="viral_posts")
    analysis = relationship("Analysis", back_populates="viral_post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ViralPost(id={self.id}, post_id={self.instagram_post_id}, score={self.viral_score})>"
