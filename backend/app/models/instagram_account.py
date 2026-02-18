import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint, Enum, LargeBinary
from sqlalchemy.orm import relationship

from app.database import Base


class AccountStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"


class InstagramAccount(Base):
    """Instagram account linked to a user."""

    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instagram_user_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    access_token = Column(LargeBinary, nullable=True)
    profile_picture = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    follower_count = Column(Integer, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    status = Column(Enum(AccountStatus), default=AccountStatus.active, nullable=False)
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
        return f"<InstagramAccount(id={self.id}, username={self.username})>"
