from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Union


class CommentBase(BaseModel):
    """Base schema with common comment fields."""
    content: str = Field(..., min_length=1, description="Comment content")


class CommentCreate(CommentBase):
    """Schema for creating a comment (request body)."""
    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment (request body)."""
    content: Optional[str] = Field(None, min_length=1, description="Comment content")


class CommentResponse(CommentBase):
    """Schema for comment response (includes all fields from DB)."""
    id: Union[int, str]  # int for PostgreSQL, str for Firestore
    post_id: Union[int, str]  # int for PostgreSQL, str for Firestore
    google_user_id: str
    author_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
