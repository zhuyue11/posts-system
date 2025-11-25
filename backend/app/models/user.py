from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    # Primary Key (using Google User ID as primary key)
    google_user_id = Column(String(255), primary_key=True, index=True)

    # User Information
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    picture = Column(String(500), nullable=True)  # Google profile picture URL

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
    )

    def __repr__(self):
        return f"<User(google_user_id={self.google_user_id}, email={self.email}, name={self.name})>"
