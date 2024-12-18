import uuid
from datetime import date, datetime
from pydantic import BaseModel


# Shared fields between models
class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


# Schema for creating a new book
class BookCreateModel(BookBase):
    pass


# Schema for updating an existing book
class BookUpdateModel(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None


# Schema for database response or API output
class Book(BookBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


