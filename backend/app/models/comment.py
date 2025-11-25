from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    # Content
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
    post = relationship("Post", back_populates="comments")

    # Indexes
    __table_args__ = (
        Index('idx_comments_post_id_created_at', 'post_id', 'created_at'),
        Index('idx_comments_google_user_id', 'google_user_id'),
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, author={self.author_name})>"
