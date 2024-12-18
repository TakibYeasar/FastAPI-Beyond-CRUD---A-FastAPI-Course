import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel
from pydantic import conint

if TYPE_CHECKING:
    from src.auth.models import User
    from src.books.models import Book


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rating: conint(ge=1, le=5) = Field(...,
                                       description="Rating between 1 and 5")
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="books.uid")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(pg.TIMESTAMP))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(
        pg.TIMESTAMP, onupdate=datetime.utcnow))

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"})
    book: Optional["Book"] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"
