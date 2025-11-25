from typing import Optional
from google.cloud import firestore
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


class FirestoreUserRepository:
    """Repository for User Firestore operations."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('users')

    def create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> UserModel:
        """Create a new user in Firestore."""
        now = firestore.SERVER_TIMESTAMP
        user_data = {
            'email': email,
            'name': name,
            'picture': picture,
            'created_at': now,
            'updated_at': now
        }
        doc_ref = self.collection.document(google_user_id)
        doc_ref.set(user_data)

        # Return user model with current timestamp
        return UserModel(
            google_user_id=google_user_id,
            email=email,
            name=name,
            picture=picture,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def get_by_google_id(self, google_user_id: str) -> Optional[UserModel]:
        """Get a user by their Google user ID."""
        doc = self.collection.document(google_user_id).get()
        if not doc.exists:
            return None

        data = doc.to_dict()
        return UserModel(
            google_user_id=doc.id,
            email=data['email'],
            name=data['name'],
            picture=data.get('picture'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by their email."""
        docs = self.collection.where('email', '==', email).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            return UserModel(
                google_user_id=doc.id,
                email=data['email'],
                name=data['name'],
                picture=data.get('picture'),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            )
        return None

    def update(self, user: UserModel, name: Optional[str] = None, picture: Optional[str] = None) -> UserModel:
        """Update a user's fields."""
        update_data = {'updated_at': firestore.SERVER_TIMESTAMP}

        if name is not None:
            update_data['name'] = name
            user.name = name
        if picture is not None:
            update_data['picture'] = picture
            user.picture = picture

        self.collection.document(user.google_user_id).update(update_data)
        user.updated_at = datetime.utcnow()
        return user

    def get_or_create(self, google_user_id: str, email: str, name: str, picture: Optional[str] = None) -> UserModel:
        """Get an existing user or create a new one."""
        user = self.get_by_google_id(google_user_id)
        if user:
            # Update user info in case it changed
            return self.update(user, name=name, picture=picture)
        return self.create(google_user_id, email, name, picture)
