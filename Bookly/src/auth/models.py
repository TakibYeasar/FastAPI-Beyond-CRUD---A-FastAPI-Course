import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.books.models import Book
    from src.reviews.models import Review


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False, unique=True))
    email: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False, unique=True))
    first_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    last_name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    role: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False), exclude=True)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, nullable=False, default=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow))

    # Relationships
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<User {self.username}>"
