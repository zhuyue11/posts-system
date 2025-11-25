from typing import List, Union
from fastapi import APIRouter, Depends, Query, status
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.post_service import PostService
from app.schemas.post import PostCreate, PostUpdate, PostResponse


router = APIRouter()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    google_user_id: str = Query(..., description="Google user ID of the post author"),
    author_name: str = Query(..., description="Name of the post author"),
    db = Depends(get_db)
):
    """
    Create a new post.

    - **subject**: Post title/subject (required)
    - **content**: Post content (required)
    - **google_user_id**: Google user ID of the post author (required)
    - **author_name**: Name of the post author (required)
    """
    service = PostService(db)
    return service.create_post(post_data, google_user_id=google_user_id, author_name=author_name)


@router.get("", response_model=List[PostResponse])
def get_all_posts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db = Depends(get_db)
):
    """
    Get all posts with pagination.

    - **skip**: Number of posts to skip (default: 0)
    - **limit**: Max number of posts to return (default: 100, max: 100)
    """
    service = PostService(db)
    return service.get_all_posts(skip=skip, limit=limit)


@router.get("/user/{google_user_id}", response_model=List[PostResponse])
def get_user_posts(
    google_user_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db = Depends(get_db)
):
    """
    Get all posts by a specific user.

    - **google_user_id**: Google user ID
    - **skip**: Number of posts to skip (default: 0)
    - **limit**: Max number of posts to return (default: 100, max: 100)
    """
    service = PostService(db)
    return service.get_user_posts(google_user_id, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: Union[int, str],
    db = Depends(get_db)
):
    """
    Get a specific post by ID.

    - **post_id**: Post ID
    """
    service = PostService(db)
    return service.get_post(post_id)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: Union[int, str],
    post_data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update a post. Only the owner can update.

    - **post_id**: Post ID
    - **subject**: New subject (optional)
    - **content**: New content (optional)

    At least one field must be provided.
    """
    service = PostService(db)
    return service.update_post(post_id, post_data, user_id=current_user["google_user_id"])


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: Union[int, str],
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a post. Only the owner can delete.
    Cascades to delete all comments on the post.

    - **post_id**: Post ID
    """
    service = PostService(db)
    service.delete_post(post_id, user_id=current_user["google_user_id"])
    return None
