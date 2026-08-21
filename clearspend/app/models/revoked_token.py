"""Store logged-out token IDs until their original expiration time."""

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True)
    token_id = Column(String(32), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
