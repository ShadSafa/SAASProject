from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class InstagramAccount(Base):
    """Instagram account linked to a user."""

    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instagram_user_id = Column(String, nullable=False)
    instagram_username = Column(String)
    access_token = Column(String)
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="instagram_accounts")

    # Table constraints
    __table_args__ = (
        Index('ix_instagram_accounts_user_id', 'user_id'),
        UniqueConstraint('user_id', 'instagram_user_id', name='uix_user_instagram'),
    )

    def __repr__(self):
        return f"<InstagramAccount(id={self.id}, username={self.instagram_username})>"
