from sqlalchemy import text
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.routes import auth_router
from books.routes import book_router
from reviews.routes import review_router
from tags.routes import tags_router
from conf.database import get_db, init_db
from src.auth.middleware import register_middleware

version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to:
- Create, read, update, and delete books
- Add reviews to books
- Add tags to books, etc.
"""

version_prefix = f"/api/{version}"

app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License",
                  "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Md Takib Yeasar",
        "url": "https://github.com/TakibYeasar",
        "email": "mdtakibyeasar@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
)

register_middleware(app)


@app.on_event("startup")
async def on_startup():
    """Initialize the database when the app starts."""
    await init_db()


@app.get("/")
async def read_root(db: AsyncSession = Depends(get_db)):
    """Test database connection."""
    try:
        # Use text() to wrap the SQL query
        result = await db.execute(text("SELECT 1"))
        return {"message": "Database connection successful", "result": result.scalar()}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}


# Include the router
app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"{version_prefix}/tags", tags=["tags"])

