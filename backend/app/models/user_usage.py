from datetime import datetime
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base


class UserUsage(Base):
    """Track user's monthly usage for quota/subscription management."""

    __tablename__ = "user_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    scans_count = Column(Integer, default=0)
    last_reset_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage")

    # Table constraints
    __table_args__ = (
        Index('ix_user_usage_user_id_month', 'user_id', 'month'),
    )

    def __repr__(self):
        return f"<UserUsage(id={self.id}, user_id={self.user_id}, month={self.month}, scans={self.scans_count})>"
