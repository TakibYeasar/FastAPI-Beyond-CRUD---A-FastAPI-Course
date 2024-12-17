from datetime import datetime
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        """Fetch all books ordered by creation date."""
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        """Fetch books for a specific user ordered by creation date."""
        statement = select(Book).where(
            Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        """Fetch a book by its UID."""
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        return result.first()  # Return None if no book is found

    async def create_book(self, book_data: BookCreateModel, user_uid: str, session: AsyncSession):
        """Create a new book."""
        # Convert the Pydantic model data into a dictionary and map it to a Book instance
        book_data_dict = book_data.model_dump()

        # Create a new book instance and set user and published date
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d")
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession):
        """Update an existing book by UID."""
        book_to_update = await self.get_book(book_uid, session)
        if not book_to_update:
            return None

        # Map the update data to the book instance
        update_data_dict = update_data.model_dump()
        for field, value in update_data_dict.items():
            setattr(book_to_update, field, value)

        await session.commit()
        return book_to_update

    async def delete_book(self, book_uid: str, session: AsyncSession):
        """Delete a book by UID."""
        book_to_delete = await self.get_book(book_uid, session)
        if not book_to_delete:
            return None

        await session.delete(book_to_delete)
        await session.commit()
        return {}

