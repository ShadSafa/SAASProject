from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    """Scan request to find viral Instagram content."""

    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_range = Column(String, nullable=True)  # "12h", "24h", "48h", "7d" — null for URL scans
    scan_type = Column(String, nullable=False, default="hashtag")  # "hashtag" or "url"
    target_url = Column(String, nullable=True)  # For url-type scans
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="scans")
    viral_posts = relationship("ViralPost", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(id={self.id}, status={self.status}, type={self.scan_type})>"
