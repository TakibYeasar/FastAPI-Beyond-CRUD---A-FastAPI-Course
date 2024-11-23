from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from .schemas import Book
from .services import BookService

book_router = APIRouter()
book_service = BookService()

