from typing import List, Optional
from google.cloud import firestore
from datetime import datetime


class PostModel:
    """Simple model class to mimic SQLAlchemy Post model."""
    def __init__(self, id: str, subject: str, content: str, google_user_id: str, author_name: str,
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.subject = subject
        self.content = content
        self.google_user_id = google_user_id
        self.author_name = author_name
        self.created_at = created_at
        self.updated_at = updated_at


class FirestorePostRepository:
    """Repository for Post Firestore operations. Each method performs ONE database operation."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('posts')

    def create(self, subject: str, content: str, google_user_id: str, author_name: str) -> PostModel:
        """Create a new post in Firestore."""
        now = firestore.SERVER_TIMESTAMP
        post_data = {
            'subject': subject,
            'content': content,
            'google_user_id': google_user_id,
            'author_name': author_name,
            'created_at': now,
            'updated_at': now
        }
        doc_ref = self.collection.document()
        doc_ref.set(post_data)

        # Return post model with current timestamp
        return PostModel(
            id=doc_ref.id,
            subject=subject,
            content=content,
            google_user_id=google_user_id,
            author_name=author_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def get_by_id(self, post_id: str) -> Optional[PostModel]:
        """Get a single post by ID."""
        doc = self.collection.document(post_id).get()
        if not doc.exists:
            return None

        data = doc.to_dict()
        return PostModel(
            id=doc.id,
            subject=data['subject'],
            content=data['content'],
            google_user_id=data['google_user_id'],
            author_name=data['author_name'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PostModel]:
        """Get all posts with pagination, ordered by created_at descending."""
        query = self.collection.order_by('created_at', direction=firestore.Query.DESCENDING).offset(skip).limit(limit)
        posts = []
        for doc in query.stream():
            data = doc.to_dict()
            posts.append(PostModel(
                id=doc.id,
                subject=data['subject'],
                content=data['content'],
                google_user_id=data['google_user_id'],
                author_name=data['author_name'],
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            ))
        return posts

    def get_by_user_id(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[PostModel]:
        """Get all posts by a specific user."""
        query = (
            self.collection
            .where('google_user_id', '==', google_user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .offset(skip)
            .limit(limit)
        )
        posts = []
        for doc in query.stream():
            data = doc.to_dict()
            posts.append(PostModel(
                id=doc.id,
                subject=data['subject'],
                content=data['content'],
                google_user_id=data['google_user_id'],
                author_name=data['author_name'],
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            ))
        return posts

    def update(self, post: PostModel, subject: Optional[str] = None, content: Optional[str] = None) -> PostModel:
        """Update a post's fields."""
        update_data = {'updated_at': firestore.SERVER_TIMESTAMP}

        if subject is not None:
            update_data['subject'] = subject
            post.subject = subject
        if content is not None:
            update_data['content'] = content
            post.content = content

        self.collection.document(post.id).update(update_data)
        post.updated_at = datetime.utcnow()
        return post

    def delete(self, post: PostModel) -> None:
        """Delete a post from Firestore. Also deletes associated comments."""
        # Delete all comments associated with this post
        comments_collection = self.db.collection('comments')
        comment_docs = comments_collection.where('post_id', '==', post.id).stream()

        # Use batch for efficient deletion
        batch = self.db.batch()
        for comment_doc in comment_docs:
            batch.delete(comment_doc.reference)

        # Delete the post itself
        batch.delete(self.collection.document(post.id))

        # Commit the batch
        batch.commit()
