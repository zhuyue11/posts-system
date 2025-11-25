from typing import Optional
from google.cloud import datastore
from datetime import datetime


class UserModel:
    """Simple model class to mimic SQLAlchemy User model."""
    def __init__(self, google_user_id: str, email: str, name: str, picture: Optional[str],
                 created_at: datetime, updated_at: datetime):
        self.google_user_id = google_user_id
        self.email = email
        self.name = name
        self.picture = picture
        self.created_at = created_at
        self.updated_at = updated_at


class DatastoreUserRepository:
    """Repository for User Datastore operations."""

    def __init__(self, db: datastore.Client):
        self.db = db
        self.kind = 'User'

    def create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> UserModel:
        """Create a new user in Datastore."""
        now = datetime.utcnow()
        key = self.db.key(self.kind, google_user_id)
        entity = datastore.Entity(key=key)
        entity.update({
            'email': email,
            'name': name,
            'picture': picture,
            'created_at': now,
            'updated_at': now
        })
        self.db.put(entity)

        return UserModel(
            google_user_id=google_user_id,
            email=email,
            name=name,
            picture=picture,
            created_at=now,
            updated_at=now
        )

    def get_by_google_id(self, google_user_id: str) -> Optional[UserModel]:
        """Get a user by their Google user ID."""
        key = self.db.key(self.kind, google_user_id)
        entity = self.db.get(key)

        if not entity:
            return None

        return UserModel(
            google_user_id=google_user_id,
            email=entity['email'],
            name=entity['name'],
            picture=entity.get('picture'),
            created_at=entity['created_at'],
            updated_at=entity['updated_at']
        )

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by their email."""
        query = self.db.query(kind=self.kind)
        query.add_filter('email', '=', email)
        results = list(query.fetch(limit=1))

        if not results:
            return None

        entity = results[0]
        return UserModel(
            google_user_id=entity.key.name,
            email=entity['email'],
            name=entity['name'],
            picture=entity.get('picture'),
            created_at=entity['created_at'],
            updated_at=entity['updated_at']
        )

    def update(self, user: UserModel) -> UserModel:
        """Update an existing user."""
        key = self.db.key(self.kind, user.google_user_id)
        entity = datastore.Entity(key=key)
        entity.update({
            'email': user.email,
            'name': user.name,
            'picture': user.picture,
            'created_at': user.created_at,
            'updated_at': datetime.utcnow()
        })
        self.db.put(entity)
        user.updated_at = datetime.utcnow()
        return user

    def get_or_create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> UserModel:
        """Get a user by Google ID, or create if it doesn't exist."""
        user = self.get_by_google_id(google_user_id)
        if user:
            return user
        return self.create(google_user_id, email, name, picture)
