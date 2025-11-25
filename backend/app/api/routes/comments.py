from typing import List, Union
from fastapi import APIRouter, Depends, Query, status
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.comment_service import CommentService
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse


router = APIRouter()


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: Union[int, str],
    comment_data: CommentCreate,
    google_user_id: str = Query(..., description="Google user ID of the comment author"),
    author_name: str = Query(..., description="Name of the comment author"),
    db = Depends(get_db)
):
    """
    Add a comment to a post.

    - **post_id**: Post ID to comment on
    - **content**: Comment content (required)
    - **google_user_id**: Google user ID of the comment author (required)
    - **author_name**: Name of the comment author (required)
    """
    service = CommentService(db)
    return service.create_comment(post_id, comment_data, google_user_id=google_user_id, author_name=author_name)


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(
    post_id: Union[int, str],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db = Depends(get_db)
):
    """
    Get all comments for a specific post.

    - **post_id**: Post ID
    - **skip**: Number of comments to skip (default: 0)
    - **limit**: Max number of comments to return (default: 100, max: 100)
    """
    service = CommentService(db)
    return service.get_post_comments(post_id, skip=skip, limit=limit)


@router.get("/comments/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: Union[int, str],
    db = Depends(get_db)
):
    """
    Get a specific comment by ID.

    - **comment_id**: Comment ID
    """
    service = CommentService(db)
    return service.get_comment(comment_id)


@router.get("/comments/user/{google_user_id}", response_model=List[CommentResponse])
def get_user_comments(
    google_user_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db = Depends(get_db)
):
    """
    Get all comments by a specific user.

    - **google_user_id**: Google user ID
    - **skip**: Number of comments to skip (default: 0)
    - **limit**: Max number of comments to return (default: 100, max: 100)
    """
    service = CommentService(db)
    return service.get_user_comments(google_user_id, skip=skip, limit=limit)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: Union[int, str],
    comment_data: CommentUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update a comment. Only the owner can update.

    - **comment_id**: Comment ID
    - **content**: New content (required)
    """
    service = CommentService(db)
    return service.update_comment(comment_id, comment_data, user_id=current_user["google_user_id"])


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: Union[int, str],
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a comment. Only the owner can delete.

    - **comment_id**: Comment ID
    """
    service = CommentService(db)
    service.delete_comment(comment_id, user_id=current_user["google_user_id"])
    return None
