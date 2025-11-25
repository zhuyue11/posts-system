from typing import List
from app.repositories import get_comment_repository, get_post_repository
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.exceptions import NotFoundError, ForbiddenError


# Default mock user constants for backward compatibility
MOCK_USER_ID = "1"
MOCK_USER_NAME = "Test User"


class CommentService:
    """Service layer for comment business logic."""

    def __init__(self, db):
        self.comment_repo = get_comment_repository(db)
        self.post_repo = get_post_repository(db)

    def create_comment(self, post_id: int, comment_data: CommentCreate, google_user_id: str = MOCK_USER_ID, author_name: str = MOCK_USER_NAME) -> CommentResponse:
        """
        Create a new comment on a post.
        Business Logic:
        - Validates post exists
        - Uses authentication data from request
        """
        # Validate post exists
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found")

        comment = self.comment_repo.create(
            post_id=post_id,
            content=comment_data.content,
            google_user_id=google_user_id,
            author_name=author_name
        )
        return CommentResponse.model_validate(comment)

    def get_comment(self, comment_id: int) -> CommentResponse:
        """
        Get a specific comment by ID.
        Business Logic: Validates comment exists.
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found")
        return CommentResponse.model_validate(comment)

    def get_post_comments(self, post_id: int, skip: int = 0, limit: int = 100) -> List[CommentResponse]:
        """
        Get all comments for a specific post.
        Business Logic: Validates post exists.
        """
        # Validate post exists
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found")

        comments = self.comment_repo.get_by_post_id(post_id, skip=skip, limit=limit)
        return [CommentResponse.model_validate(comment) for comment in comments]

    def get_user_comments(self, google_user_id: str, skip: int = 0, limit: int = 100) -> List[CommentResponse]:
        """Get all comments by a specific user."""
        comments = self.comment_repo.get_by_user_id(google_user_id, skip=skip, limit=limit)
        return [CommentResponse.model_validate(comment) for comment in comments]

    def update_comment(self, comment_id: int, comment_data: CommentUpdate, user_id: str = MOCK_USER_ID) -> CommentResponse:
        """
        Update a comment.
        Business Logic:
        - Validates comment exists
        - Validates user owns the comment
        - Validates content is provided
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found")

        # Validate ownership
        if comment.google_user_id != user_id:
            raise ForbiddenError("You don't have permission to update this comment")

        # Validate content is provided
        if comment_data.content is None:
            raise ValueError("Content must be provided for update")

        updated_comment = self.comment_repo.update(
            comment=comment,
            content=comment_data.content
        )
        return CommentResponse.model_validate(updated_comment)

    def delete_comment(self, comment_id: int, user_id: str = MOCK_USER_ID) -> None:
        """
        Delete a comment.
        Business Logic:
        - Validates comment exists
        - Validates user owns the comment
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found")

        # Validate ownership
        if comment.google_user_id != user_id:
            raise ForbiddenError("You don't have permission to delete this comment")

        self.comment_repo.delete(comment)
