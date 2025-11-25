from typing import List
from app.repositories import get_post_repository, get_comment_repository
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.exceptions import NotFoundError, ForbiddenError


# Default mock user constants for backward compatibility
MOCK_USER_ID = "1"
MOCK_USER_NAME = "Test User"


class PostService:
    """Service layer for post business logic."""

    def __init__(self, db):
        self.repository = get_post_repository(db)
        self.comment_repository = get_comment_repository(db)

    def create_post(self, post_data: PostCreate, google_user_id: str = MOCK_USER_ID, author_name: str = MOCK_USER_NAME) -> PostResponse:
        """
        Create a new post.
        Business Logic: Uses authentication data from request.
        """
        post = self.repository.create(
            subject=post_data.subject,
            content=post_data.content,
            google_user_id=google_user_id,
            author_name=author_name
        )
        return PostResponse.model_validate(post)

    def get_post(self, post_id: int) -> PostResponse:
        """
        Get a specific post by ID.
        Business Logic: Validates post exists.
        """
        post = self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found")
        return PostResponse.model_validate(post)

    def get_all_posts(self, skip: int = 0, limit: int = 100) -> List[PostResponse]:
        """Get all posts with pagination."""
        posts = self.repository.get_all(skip=skip, limit=limit)
        responses = []
        for post in posts:
            response = PostResponse.model_validate(post)
            # Get comment count using repository (works for both PostgreSQL and Firestore)
            response.comment_count = self.comment_repository.count_by_post_id(post.id)
            responses.append(response)
        return responses

    def get_user_posts(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[PostResponse]:
        """Get all posts by a specific user."""
        posts = self.repository.get_by_user_id(google_user_id, skip=skip, limit=limit)
        return [PostResponse.model_validate(post) for post in posts]

    def update_post(self, post_id: int, post_data: PostUpdate, user_id: str = MOCK_USER_ID) -> PostResponse:
        """
        Update a post.
        Business Logic:
        - Validates post exists
        - Validates user owns the post
        - Validates at least one field is being updated
        """
        post = self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found")

        # Validate ownership
        if post.google_user_id != user_id:
            raise ForbiddenError("You don't have permission to update this post")

        # Validate at least one field is being updated
        if post_data.subject is None and post_data.content is None:
            raise ValueError("At least one field (subject or content) must be provided for update")

        updated_post = self.repository.update(
            post=post,
            subject=post_data.subject,
            content=post_data.content
        )
        return PostResponse.model_validate(updated_post)

    def delete_post(self, post_id: int, user_id: str = MOCK_USER_ID) -> None:
        """
        Delete a post.
        Business Logic:
        - Validates post exists
        - Validates user owns the post
        - Cascades to delete comments (handled by DB)
        """
        post = self.repository.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found")

        # Validate ownership
        if post.google_user_id != user_id:
            raise ForbiddenError("You don't have permission to delete this post")

        self.repository.delete(post)
