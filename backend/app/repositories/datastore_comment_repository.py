from typing import List, Optional
from google.cloud import datastore
from datetime import datetime
import uuid


class CommentModel:
    """Simple model class to mimic SQLAlchemy Comment model."""
    def __init__(self, id: str, post_id: str, google_user_id: str, author_name: str, content: str,
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.post_id = post_id
        self.google_user_id = google_user_id
        self.author_name = author_name
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at


class DatastoreCommentRepository:
    """Repository for Comment Datastore operations."""

    def __init__(self, db: datastore.Client):
        self.db = db
        self.kind = 'Comment'

    def create(self, post_id: str, google_user_id: str, author_name: str, content: str) -> CommentModel:
        """Create a new comment in Datastore."""
        now = datetime.utcnow()
        comment_id = str(uuid.uuid4())
        key = self.db.key(self.kind, comment_id)
        entity = datastore.Entity(key=key)
        entity.update({
            'post_id': post_id,
            'google_user_id': google_user_id,
            'author_name': author_name,
            'content': content,
            'created_at': now,
            'updated_at': now
        })
        self.db.put(entity)

        return CommentModel(
            id=comment_id,
            post_id=post_id,
            google_user_id=google_user_id,
            author_name=author_name,
            content=content,
            created_at=now,
            updated_at=now
        )

    def get_by_id(self, comment_id: str) -> Optional[CommentModel]:
        """Get a comment by ID."""
        key = self.db.key(self.kind, comment_id)
        entity = self.db.get(key)

        if not entity:
            return None

        return CommentModel(
            id=comment_id,
            post_id=entity['post_id'],
            google_user_id=entity['google_user_id'],
            author_name=entity['author_name'],
            content=entity['content'],
            created_at=entity['created_at'],
            updated_at=entity['updated_at']
        )

    def get_by_post_id(self, post_id: str, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get comments for a post ordered by created_at ascending."""
        query = self.db.query(kind=self.kind)
        query.add_filter('post_id', '=', post_id)
        query.order = ['created_at']
        results = list(query.fetch(limit=limit, offset=skip))

        return [
            CommentModel(
                id=entity.key.name,
                post_id=entity['post_id'],
                google_user_id=entity['google_user_id'],
                author_name=entity['author_name'],
                content=entity['content'],
                created_at=entity['created_at'],
                updated_at=entity['updated_at']
            )
            for entity in results
        ]

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get comments by user ordered by created_at descending."""
        query = self.db.query(kind=self.kind)
        query.add_filter('google_user_id', '=', google_user_id)
        query.order = ['-created_at']
        results = list(query.fetch(limit=limit, offset=skip))

        return [
            CommentModel(
                id=entity.key.name,
                post_id=entity['post_id'],
                google_user_id=entity['google_user_id'],
                author_name=entity['author_name'],
                content=entity['content'],
                created_at=entity['created_at'],
                updated_at=entity['updated_at']
            )
            for entity in results
        ]

    def update(self, comment: CommentModel, content: str) -> CommentModel:
        """Update an existing comment."""
        key = self.db.key(self.kind, comment.id)
        entity = datastore.Entity(key=key)
        entity.update({
            'post_id': comment.post_id,
            'google_user_id': comment.google_user_id,
            'author_name': comment.author_name,
            'content': content,
            'created_at': comment.created_at,
            'updated_at': datetime.utcnow()
        })
        self.db.put(entity)
        comment.content = content
        comment.updated_at = datetime.utcnow()
        return comment

    def delete(self, comment: CommentModel) -> None:
        """Delete a comment."""
        key = self.db.key(self.kind, comment.id)
        self.db.delete(key)

    def count_by_post_id(self, post_id: str) -> int:
        """Count comments for a specific post."""
        query = self.db.query(kind=self.kind)
        query.add_filter('post_id', '=', post_id)
        query.keys_only()
        results = list(query.fetch())
        return len(results)
