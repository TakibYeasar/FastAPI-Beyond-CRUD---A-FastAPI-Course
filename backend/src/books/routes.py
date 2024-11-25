from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from auth.dependencies import AccessTokenBearer, RoleChecker
from .services import BookService
from src.main import get_session
from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel

book_router = APIRouter()
book_service = BookService()

# Define common dependencies
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Fetch all books."""
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Fetch books submitted by a specific user."""
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> Book:
    """Create a new book."""
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
) -> BookDetailModel:
    """Fetch details of a specific book by its UID."""
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
    )


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
) -> Book:
    """Update an existing book."""
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book:
        return updated_book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
    )


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Delete a book by UID."""
    deleted_book = await book_service.delete_book(book_uid, session)

    if not deleted_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )
    return {}
