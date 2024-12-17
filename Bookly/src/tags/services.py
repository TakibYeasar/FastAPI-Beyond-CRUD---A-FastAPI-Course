from fastapi import HTTPException, status
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from books.services import BookService
from .models import Tag
from .schemas import TagAddModel, TagCreateModel

book_service = BookService()


class TagService:
    """Service class to manage tags and their association with books."""

    async def get_tags(self, session: AsyncSession) -> list[Tag]:
        """
        Retrieve all tags ordered by creation date (latest first).
        """
        try:
            statement = select(Tag).order_by(desc(Tag.created_at))
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tags.",
            ) from e

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession) -> Tag:
        """
        Retrieve a tag by its unique identifier.
        """
        try:
            statement = select(Tag).where(Tag.uid == tag_uid)
            result = await session.exec(statement)
            tag = result.first()
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tag with UID {tag_uid} not found.",
                )
            return tag
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve the tag.",
            ) from e

    async def get_tag_by_name(self, tag_name: str, session: AsyncSession) -> Tag | None:
        """
        Retrieve a tag by its name.
        """
        try:
            statement = select(Tag).where(Tag.name == tag_name)
            result = await session.exec(statement)
            return result.one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tag by name.",
            ) from e

    async def add_tags_to_book(self, book_uid: str, tag_data: TagAddModel, session: AsyncSession) -> object:
        """
        Associate multiple tags with a book. Creates new tags if they don't exist.
        """
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with UID {book_uid} not found.",
                )

            # Add existing or create new tags
            new_tags = []
            for tag_item in tag_data.tags:
                tag = await self.get_tag_by_name(tag_item.name, session)
                if not tag:
                    tag = Tag(name=tag_item.name)
                    new_tags.append(tag)
                book.tags.append(tag)

            session.add_all(new_tags)
            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to associate tags with the book.",
            ) from e

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession) -> Tag:
        """
        Create a new tag if it doesn't already exist.
        """
        try:
            tag = await self.get_tag_by_name(tag_data.name, session)
            if tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tag with name '{tag_data.name}' already exists.",
                )

            new_tag = Tag(name=tag_data.name)
            session.add(new_tag)
            await session.commit()
            return new_tag
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create a new tag.",
            ) from e

    async def update_tag(self, tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession) -> Tag:
        """
        Update a tag's information.
        """
        try:
            tag = await self.get_tag_by_uid(tag_uid, session)
            update_data = tag_update_data.model_dump()

            for field, value in update_data.items():
                setattr(tag, field, value)

            session.add(tag)
            await session.commit()
            await session.refresh(tag)
            return tag
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update the tag.",
            ) from e

    async def delete_tag(self, tag_uid: str, session: AsyncSession) -> None:
        """
        Delete a tag by its unique identifier.
        """
        try:
            tag = await self.get_tag_by_uid(tag_uid, session)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tag with UID {tag_uid} not found.",
                )

            await session.delete(tag)
            await session.commit()
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete the tag.",
            ) from e
