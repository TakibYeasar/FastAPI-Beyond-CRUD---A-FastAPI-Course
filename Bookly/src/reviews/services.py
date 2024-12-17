import logging
from fastapi import status, HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from auth.services import UserService
from books.services import BookService
from .models import Review
from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            # Fetch user and book using helper function
            book, user = await self._get_user_and_book_by_email(user_email, book_uid, session)

            # Validate review data
            if not review_data.rating or not (1 <= review_data.rating <= 5):
                raise HTTPException(
                    detail="Invalid rating, it should be between 1 and 5.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            new_review = Review(**review_data.dict(), user=user, book=book)
            session.add(new_review)
            await session.commit()

            logging.info(f"Review added for book {
                         book_uid} by user {user_email}")
            return new_review

        except HTTPException as e:
            # Specific HTTP exceptions are raised earlier, so we can let them pass through
            raise e

        except Exception as e:
            logging.exception("Error occurred while adding review")
            raise HTTPException(
                detail="Oops... something went wrong while adding the review!",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def get_review(self, review_uid: str, session: AsyncSession):
        try:
            statement = select(Review).where(Review.uid == review_uid)
            result = await session.exec(statement)
            review = result.first()

            if not review:
                raise HTTPException(
                    detail="Review not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return review

        except Exception as e:
            logging.exception(f"Error fetching review with UID {review_uid}")
            raise HTTPException(
                detail="Error fetching review.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def get_all_reviews(self, session: AsyncSession):
        try:
            statement = select(Review).order_by(desc(Review.created_at))
            result = await session.exec(statement)
            return result.all()

        except Exception as e:
            logging.exception("Error fetching all reviews")
            raise HTTPException(
                detail="Error fetching reviews.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def delete_review_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        try:
            # Fetch user and review
            user = await user_service.get_user_by_email(user_email, session)
            review = await self.get_review(review_uid, session)

            if not review or review.user != user:
                raise HTTPException(
                    detail="You do not have permission to delete this review.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            session.delete(review)
            await session.commit()

            logging.info(f"Review {review_uid} deleted by user {user_email}")
            return {"message": "Review deleted successfully"}

        except HTTPException as e:
            raise e

        except Exception as e:
            logging.exception(f"Error deleting review with UID {review_uid}")
            raise HTTPException(
                detail="Error occurred while deleting the review.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Helper method to fetch user and book by email and book UID
    async def _get_user_and_book_by_email(self, user_email: str, book_uid: str, session: AsyncSession):
        book = await book_service.get_book(book_uid=book_uid, session=session)
        user = await user_service.get_user_by_email(email=user_email, session=session)

        if not book:
            raise HTTPException(
                detail="Book not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not user:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return book, user
