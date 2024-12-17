import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker, get_current_user
from src.conf.database import get_db
from auth.models import User
from .schemas import ReviewCreateModel
from .services import ReviewService

review_service = ReviewService()
review_router = APIRouter()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get("/", response_model=list, dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_db)):
    try:
        reviews = await review_service.get_all_reviews(session)
        return reviews
    except Exception as e:
        logging.error(f"Error fetching all reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching reviews. Please try again later.",
        )


@review_router.get("/{review_uid}", response_model=ReviewCreateModel, dependencies=[user_role_checker])
async def get_review(
    review_uid: str, session: AsyncSession = Depends(get_db)
):
    try:
        review = await review_service.get_review(review_uid, session)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with UID {review_uid} not found.",
            )
        return review
    except HTTPException as e:
        # Re-raise the HTTPException if it's a custom exception
        raise e
    except Exception as e:
        logging.error(f"Error fetching review {review_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching the review. Please try again later.",
        )


@review_router.post("/book/{book_uid}", response_model=ReviewCreateModel, dependencies=[user_role_checker])
async def add_review_to_books(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        new_review = await review_service.add_review_to_book(
            user_email=current_user.email,
            review_data=review_data,
            book_uid=book_uid,
            session=session,
        )
        logging.info(f"Review added for book {
                     book_uid} by user {current_user.email}")
        return new_review
    except HTTPException as e:
        # Handle any custom HTTPException raised from the service
        raise e
    except Exception as e:
        logging.error(f"Error adding review for book {
                      book_uid} by user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding the review. Please try again later.",
        )


@review_router.delete(
    "/{review_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        await review_service.delete_review_from_book(
            review_uid=review_uid, user_email=current_user.email, session=session
        )
        logging.info(f"Review {review_uid} deleted by user {
                     current_user.email}")
        return None
    except HTTPException as e:
        # Handle any custom HTTPException raised from the service
        raise e
    except Exception as e:
        logging.error(f"Error deleting review {review_uid} by user {
                      current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting the review. Please try again later.",
        )
