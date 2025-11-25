from typing import List, Optional
from google.cloud import datastore
from datetime import datetime
import uuid


class PostModel:
    """Simple model class to mimic SQLAlchemy Post model."""
    def __init__(self, id: str, google_user_id: str, author_name: str, subject: str, content: str,
                 created_at: datetime, updated_at: datetime, comment_count: int = 0):
        self.id = id
        self.google_user_id = google_user_id
        self.author_name = author_name
        self.subject = subject
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at
        self.comment_count = comment_count


class DatastorePostRepository:
    """Repository for Post Datastore operations."""

    def __init__(self, db: datastore.Client):
        self.db = db
        self.kind = 'Post'

    def create(self, google_user_id: str, author_name: str, subject: str, content: str) -> PostModel:
        """Create a new post in Datastore."""
        now = datetime.utcnow()
        post_id = str(uuid.uuid4())
        key = self.db.key(self.kind, post_id)
        entity = datastore.Entity(key=key)
        entity.update({
            'google_user_id': google_user_id,
            'author_name': author_name,
            'subject': subject,
            'content': content,
            'created_at': now,
            'updated_at': now,
            'comment_count': 0
        })
        self.db.put(entity)

        return PostModel(
            id=post_id,
            google_user_id=google_user_id,
            author_name=author_name,
            subject=subject,
            content=content,
            created_at=now,
            updated_at=now,
            comment_count=0
        )

    def get_by_id(self, post_id: str) -> Optional[PostModel]:
        """Get a post by ID."""
        key = self.db.key(self.kind, post_id)
        entity = self.db.get(key)

        if not entity:
            return None

        return PostModel(
            id=post_id,
            google_user_id=entity['google_user_id'],
            author_name=entity['author_name'],
            subject=entity['subject'],
            content=entity['content'],
            created_at=entity['created_at'],
            updated_at=entity['updated_at'],
            comment_count=entity.get('comment_count', 0)
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PostModel]:
        """Get all posts ordered by created_at descending."""
        query = self.db.query(kind=self.kind)
        query.order = ['-created_at']
        results = list(query.fetch(limit=limit, offset=skip))

        return [
            PostModel(
                id=entity.key.name,
                google_user_id=entity['google_user_id'],
                author_name=entity['author_name'],
                subject=entity['subject'],
                content=entity['content'],
                created_at=entity['created_at'],
                updated_at=entity['updated_at'],
                comment_count=entity.get('comment_count', 0)
            )
            for entity in results
        ]

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[PostModel]:
        """Get posts by user ordered by created_at descending."""
        query = self.db.query(kind=self.kind)
        query.add_filter('google_user_id', '=', google_user_id)
        query.order = ['-created_at']
        results = list(query.fetch(limit=limit, offset=skip))

        return [
            PostModel(
                id=entity.key.name,
                google_user_id=entity['google_user_id'],
                author_name=entity['author_name'],
                subject=entity['subject'],
                content=entity['content'],
                created_at=entity['created_at'],
                updated_at=entity['updated_at'],
                comment_count=entity.get('comment_count', 0)
            )
            for entity in results
        ]

    def update(self, post: PostModel, subject: Optional[str] = None, content: Optional[str] = None) -> PostModel:
        """Update an existing post."""
        if subject is not None:
            post.subject = subject
        if content is not None:
            post.content = content

        key = self.db.key(self.kind, post.id)
        entity = datastore.Entity(key=key)
        entity.update({
            'google_user_id': post.google_user_id,
            'author_name': post.author_name,
            'subject': post.subject,
            'content': post.content,
            'created_at': post.created_at,
            'updated_at': datetime.utcnow(),
            'comment_count': post.comment_count
        })
        self.db.put(entity)
        post.updated_at = datetime.utcnow()
        return post

    def delete(self, post: PostModel) -> None:
        """Delete a post and all its comments (CASCADE)."""
        # First, delete all comments associated with this post
        comment_query = self.db.query(kind='Comment')
        comment_query.add_filter('post_id', '=', post.id)
        comment_keys = [entity.key for entity in comment_query.fetch()]

        # Delete comments and post in a batch
        keys_to_delete = comment_keys + [self.db.key(self.kind, post.id)]
        self.db.delete_multi(keys_to_delete)

    def increment_comment_count(self, post_id: str) -> None:
        """Increment the comment count for a post."""
        key = self.db.key(self.kind, post_id)
        entity = self.db.get(key)
        if entity:
            entity['comment_count'] = entity.get('comment_count', 0) + 1
            self.db.put(entity)

    def decrement_comment_count(self, post_id: str) -> None:
        """Decrement the comment count for a post."""
        key = self.db.key(self.kind, post_id)
        entity = self.db.get(key)
        if entity and entity.get('comment_count', 0) > 0:
            entity['comment_count'] = entity['comment_count'] - 1
            self.db.put(entity)
