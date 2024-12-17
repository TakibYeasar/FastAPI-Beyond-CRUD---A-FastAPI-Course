import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

# Use TYPE_CHECKING to avoid runtime circular imports
if TYPE_CHECKING:
    from src.auth.models import User
    from src.books.models import Book


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(le=5, ge=1, nullable=False)  # Rating between 1 and 5
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid"
    )
    book_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="books.uid"
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
        )
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"


