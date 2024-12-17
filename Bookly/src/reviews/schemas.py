import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(ge=1, le=5)  # Rating between 1 and 5
    review_text: str
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime  # Fixed typo `update_at` to `updated_at`

    class Config:
        orm_mode = True  # This allows Pydantic to read data from SQLAlchemy models


class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)  # Rating between 1 and 5
    review_text: str

    class Config:
        orm_mode = True  # This allows Pydantic to read data from SQLAlchemy models
