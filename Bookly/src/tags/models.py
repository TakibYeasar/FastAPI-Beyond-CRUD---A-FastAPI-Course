import uuid
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel
from books.models import Book

# Use TYPE_CHECKING to avoid runtime circular imports
if TYPE_CHECKING:
    from src.auth.models import User
    from src.reviews.models import Review
    from src.books.models import BookTag, Tag


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
