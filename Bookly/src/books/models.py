from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, date
import uuid
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.auth.models import User
    from src.reviews.models import Review


class BookTag(SQLModel, table=True):
    __tablename__ = "book_tags"

    # Composite primary key: book_id and tag_id
    book_id: uuid.UUID = Field(
        default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(
        default=None, foreign_key="tags.uid", primary_key=True)

    # Relationships
    book: "Book" = Relationship(back_populates="tags")
    tag: "Tag" = Relationship(back_populates="books")


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    author: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    publisher: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    published_date: date = Field(sa_column=Column(pg.DATE, nullable=False))
    page_count: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    language: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(pg.TIMESTAMP))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(
        pg.TIMESTAMP, onupdate=datetime.utcnow))

    # Relationships
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})
    tags: List["Tag"] = Relationship(
        link_model=BookTag, back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False, unique=True))
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(pg.TIMESTAMP))

    # Relationship: Many-to-many with Book via BookTag
    books: List["Book"] = Relationship(
        link_model=BookTag, back_populates="tag", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
