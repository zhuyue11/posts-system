from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Content
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # User Information (for future Google OAuth)
    google_user_id = Column(String(255), nullable=False)
    author_name = Column(String(100), nullable=False)

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

    # Relationships
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",  # Delete comments when post is deleted
        lazy="selectin"  # Eager loading for better performance
    )

    # Indexes
    __table_args__ = (
        Index('idx_posts_created_at', 'created_at'),
        Index('idx_posts_google_user_id', 'google_user_id'),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, author={self.author_name}, content={self.content[:30]}...)>"
