import uuid
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

# Use TYPE_CHECKING to avoid runtime circular imports
if TYPE_CHECKING:
    from src.auth.models import User
    from src.reviews.models import Review
    from src.books.models import BookTag, Tag


class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(
        default=None, foreign_key="books.uid", primary_key=True
    )
    tag_id: uuid.UUID = Field(
        default=None, foreign_key="tags.uid", primary_key=True
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, unique=True)
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )

    # Relationship
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    title: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    author: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    publisher: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    published_date: date = Field(sa_column=Column(pg.DATE, nullable=False))
    page_count: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    language: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid"
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
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List[Tag] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Book {self.title}>"
