from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.post import Post


class PostRepository:
    """Repository for Post database operations. Each method performs ONE database operation."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, subject: str, content: str, google_user_id: str, author_name: str) -> Post:
        """Create a new post in the database."""
        post = Post(
            subject=subject,
            content=content,
            google_user_id=google_user_id,
            author_name=author_name
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get a single post by ID."""
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get all posts with pagination."""
        return self.db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get all posts by a specific user."""
        return (
            self.db.query(Post)
            .filter(Post.google_user_id == google_user_id)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, post: Post, subject: Optional[str] = None, content: Optional[str] = None) -> Post:
        """Update a post's fields."""
        if subject is not None:
            post.subject = subject
        if content is not None:
            post.content = content
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        """Delete a post from the database."""
        self.db.delete(post)
        self.db.commit()
