from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.comment import Comment


class CommentRepository:
    """Repository for Comment database operations. Each method performs ONE database operation."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, post_id: int, content: str, google_user_id: str, author_name: str) -> Comment:
        """Create a new comment in the database."""
        comment = Comment(
            post_id=post_id,
            content=content,
            google_user_id=google_user_id,
            author_name=author_name
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get a single comment by ID."""
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_by_post_id(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get all comments for a specific post."""
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())  # Oldest first for comments
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get all comments by a specific user."""
        return (
            self.db.query(Comment)
            .filter(Comment.google_user_id == google_user_id)
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, comment: Comment, content: str) -> Comment:
        """Update a comment's content."""
        comment.content = content
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        """Delete a comment from the database."""
        self.db.delete(comment)
        self.db.commit()
