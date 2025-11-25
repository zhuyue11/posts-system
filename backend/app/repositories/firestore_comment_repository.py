from typing import List, Optional
from google.cloud import firestore
from datetime import datetime


class CommentModel:
    """Simple model class to mimic SQLAlchemy Comment model."""
    def __init__(self, id: str, post_id: str, content: str, google_user_id: str, author_name: str,
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.post_id = post_id
        self.content = content
        self.google_user_id = google_user_id
        self.author_name = author_name
        self.created_at = created_at
        self.updated_at = updated_at


class FirestoreCommentRepository:
    """Repository for Comment Firestore operations. Each method performs ONE database operation."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('comments')

    def create(self, post_id: str, content: str, google_user_id: str, author_name: str) -> CommentModel:
        """Create a new comment in Firestore."""
        now = firestore.SERVER_TIMESTAMP
        comment_data = {
            'post_id': post_id,
            'content': content,
            'google_user_id': google_user_id,
            'author_name': author_name,
            'created_at': now,
            'updated_at': now
        }
        doc_ref = self.collection.document()
        doc_ref.set(comment_data)

        # Return comment model with current timestamp
        return CommentModel(
            id=doc_ref.id,
            post_id=post_id,
            content=content,
            google_user_id=google_user_id,
            author_name=author_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def get_by_id(self, comment_id: str) -> Optional[CommentModel]:
        """Get a single comment by ID."""
        doc = self.collection.document(comment_id).get()
        if not doc.exists:
            return None

        data = doc.to_dict()
        return CommentModel(
            id=doc.id,
            post_id=data['post_id'],
            content=data['content'],
            google_user_id=data['google_user_id'],
            author_name=data['author_name'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def get_by_post_id(self, post_id: str, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get all comments for a specific post, ordered by created_at ascending (oldest first)."""
        query = (
            self.collection
            .where('post_id', '==', post_id)
            .order_by('created_at', direction=firestore.Query.ASCENDING)
            .offset(skip)
            .limit(limit)
        )
        comments = []
        for doc in query.stream():
            data = doc.to_dict()
            comments.append(CommentModel(
                id=doc.id,
                post_id=data['post_id'],
                content=data['content'],
                google_user_id=data['google_user_id'],
                author_name=data['author_name'],
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            ))
        return comments

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        """Get all comments by a specific user, ordered by created_at descending."""
        query = (
            self.collection
            .where('google_user_id', '==', google_user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .offset(skip)
            .limit(limit)
        )
        comments = []
        for doc in query.stream():
            data = doc.to_dict()
            comments.append(CommentModel(
                id=doc.id,
                post_id=data['post_id'],
                content=data['content'],
                google_user_id=data['google_user_id'],
                author_name=data['author_name'],
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            ))
        return comments

    def update(self, comment: CommentModel, content: str) -> CommentModel:
        """Update a comment's content."""
        update_data = {
            'content': content,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        self.collection.document(comment.id).update(update_data)
        comment.content = content
        comment.updated_at = datetime.utcnow()
        return comment

    def count_by_post_id(self, post_id: str) -> int:
        """Count comments for a specific post."""
        query = self.collection.where('post_id', '==', post_id)
        # Get all matching documents and count them
        count = sum(1 for _ in query.stream())
        return count

    def delete(self, comment: CommentModel) -> None:
        """Delete a comment from Firestore."""
        self.collection.document(comment.id).delete()
