from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> User:
        """Create a new user in the database."""
        user = User(
            google_user_id=google_user_id,
            email=email,
            name=name,
            picture=picture
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_google_id(self, google_user_id: str) -> Optional[User]:
        """Get a user by their Google user ID."""
        return self.db.query(User).filter(User.google_user_id == google_user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user: User, name: Optional[str] = None, picture: Optional[str] = None) -> User:
        """Update a user's fields."""
        if name is not None:
            user.name = name
        if picture is not None:
            user.picture = picture
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> User:
        """Get an existing user or create a new one."""
        user = self.get_by_google_id(google_user_id)
        if user:
            # Update user info in case it changed
            return self.update(user, name=name, picture=picture)
        return self.create(google_user_id, email, name, picture)
