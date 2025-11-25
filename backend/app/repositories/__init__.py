from app.repositories.post_repository import PostRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.firestore_post_repository import FirestorePostRepository
from app.repositories.firestore_comment_repository import FirestoreCommentRepository
from app.repositories.firestore_user_repository import FirestoreUserRepository
from app.repositories.datastore_post_repository import DatastorePostRepository
from app.repositories.datastore_comment_repository import DatastoreCommentRepository
from app.repositories.datastore_user_repository import DatastoreUserRepository
from app.core.config import settings

__all__ = ["PostRepository", "CommentRepository", "UserRepository",
           "FirestorePostRepository", "FirestoreCommentRepository", "FirestoreUserRepository",
           "DatastorePostRepository", "DatastoreCommentRepository", "DatastoreUserRepository",
           "get_user_repository", "get_post_repository", "get_comment_repository"]


def get_user_repository(db):
    """Factory function to get the appropriate user repository based on DB_TYPE."""
    if settings.DB_TYPE == "postgresql":
        return UserRepository(db)
    elif settings.DB_TYPE == "firestore":
        return DatastoreUserRepository(db)
    else:
        raise ValueError(f"Unknown DB_TYPE: {settings.DB_TYPE}")


def get_post_repository(db):
    """Factory function to get the appropriate post repository based on DB_TYPE."""
    if settings.DB_TYPE == "postgresql":
        return PostRepository(db)
    elif settings.DB_TYPE == "firestore":
        return DatastorePostRepository(db)
    else:
        raise ValueError(f"Unknown DB_TYPE: {settings.DB_TYPE}")


def get_comment_repository(db):
    """Factory function to get the appropriate comment repository based on DB_TYPE."""
    if settings.DB_TYPE == "postgresql":
        return CommentRepository(db)
    elif settings.DB_TYPE == "firestore":
        return DatastoreCommentRepository(db)
    else:
        raise ValueError(f"Unknown DB_TYPE: {settings.DB_TYPE}")
