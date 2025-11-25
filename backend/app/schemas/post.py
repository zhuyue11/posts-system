from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    """Base schema with common post fields."""
    subject: str = Field(..., min_length=1, max_length=255, description="Post subject/title")
    content: str = Field(..., min_length=1, description="Post content")


class PostCreate(PostBase):
    """Schema for creating a post (request body)."""
    pass


class PostUpdate(BaseModel):
    """Schema for updating a post (request body). All fields optional for partial updates."""
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Post subject/title")
    content: Optional[str] = Field(None, min_length=1, description="Post content")


class PostResponse(PostBase):
    """Schema for post response (includes all fields from DB)."""
    id: int
    google_user_id: str
    author_name: str
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0

    model_config = ConfigDict(from_attributes=True)
