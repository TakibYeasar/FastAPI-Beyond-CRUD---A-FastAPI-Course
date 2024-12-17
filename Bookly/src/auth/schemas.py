import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, EmailStr
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    first_name: str = Field(..., max_length=25, example="John")
    last_name: str = Field(..., max_length=25, example="Doe")
    username: str = Field(..., max_length=8, example="johndoe")
    email: EmailStr = Field(..., example="johndoe123@co.com")
    password: str = Field(..., min_length=6, example="testpass123")

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe123@co.com",
                "password": "testpass123",
            }
        }


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email: EmailStr = Field(..., example="johndoe123@co.com")
    password: str = Field(..., min_length=6, example="testpass123")


class EmailModel(BaseModel):
    addresses: List[EmailStr]

    class Config:
        schema_extra = {
            "example": {
                "addresses": [
                    "user1@example.com",
                    "user2@example.com"
                ]
            }
        }


class PasswordResetRequestModel(BaseModel):
    email: EmailStr = Field(..., example="johndoe123@co.com")

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe123@co.com",
            }
        }


class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(..., min_length=6, example="newpass123")
    confirm_new_password: str = Field(..., min_length=6, example="newpass123")

    class Config:
        schema_extra = {
            "example": {
                "new_password": "newpass123",
                "confirm_new_password": "newpass123",
            }
        }
