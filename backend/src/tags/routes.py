from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker
from src.books.schemas import Book
from conf.database import get_db
from .schemas import TagAddModel, TagCreateModel, TagModel
from .services import TagService

tags_router = APIRouter(prefix="/tags", tags=["Tags"])
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tags_router.get(
    "/",
    response_model=List[TagModel],
    status_code=status.HTTP_200_OK,
    dependencies=[user_role_checker],
)
async def get_all_tags(session: AsyncSession = Depends(get_db)) -> List[TagModel]:
    """
    Retrieve all tags.
    """
    tags = await tag_service.get_tags(session)
    if not tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No tags found."
        )
    return tags


@tags_router.post(
    "/",
    response_model=TagModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[user_role_checker],
)
async def add_tag(
    tag_data: TagCreateModel, session: AsyncSession = Depends(get_db)
) -> TagModel:
    """
    Add a new tag.
    """
    try:
        tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)
        return tag_added
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the tag.",
        )


@tags_router.post(
    "/book/{book_uid}/tags",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    dependencies=[user_role_checker],
)
async def add_tags_to_book(
    book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_db)
) -> Book:
    """
    Add tags to a book. Creates new tags if they don't exist.
    """
    try:
        book_with_tag = await tag_service.add_tags_to_book(
            book_uid=book_uid, tag_data=tag_data, session=session
        )
        return book_with_tag
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding tags to the book.",
        )


@tags_router.put(
    "/{tag_uid}",
    response_model=TagModel,
    status_code=status.HTTP_200_OK,
    dependencies=[user_role_checker],
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateModel,
    session: AsyncSession = Depends(get_db),
) -> TagModel:
    """
    Update a tag's details.
    """
    try:
        updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)
        return updated_tag
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the tag.",
        )


@tags_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def delete_tag(
    tag_uid: str, session: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a tag by its unique identifier.
    """
    try:
        await tag_service.delete_tag(tag_uid, session)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the tag.",
        )
