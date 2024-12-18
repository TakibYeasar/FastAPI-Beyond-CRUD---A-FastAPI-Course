from sqlalchemy import text
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# from auth.routes import auth_router
# from books.routes import book_router
# from reviews.routes import review_router
# from tags.routes import tags_router
from conf.database import get_db, init_db
# from auth.middleware import register_middleware

# Define the API version
API_VERSION = "v1"
VERSION_PREFIX = f"/api/{API_VERSION}"

# Define the application description
DESCRIPTION = """
A REST API for a book review web service.

This REST API supports:
- Managing books (create, read, update, delete)
- Adding reviews to books
- Associating tags with books, etc.
"""

# FastAPI app instance
app = FastAPI(
    title="Bookly",
    description=DESCRIPTION,
    version=API_VERSION,
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit",
    },
    contact={
        "name": "Md Takib Yeasar",
        "url": "https://github.com/TakibYeasar",
        "email": "mdtakibyeasar@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{VERSION_PREFIX}/openapi.json",
    docs_url=f"{VERSION_PREFIX}/docs",
    redoc_url=f"{VERSION_PREFIX}/redoc",
)

# Register middleware
# register_middleware(app)


@app.on_event("startup")
async def on_startup():
    """Initialize the database when the application starts."""
    await init_db()


@app.get("/", summary="Test Database Connection")
async def read_root(db: AsyncSession = Depends(get_db)):
    """
    Test the database connection by executing a simple query.
    """
    try:
        # Execute a simple query to validate the database connection
        result = await db.execute(text("SELECT 1"))
        return {"message": "Database connection successful", "result": result.scalar()}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}


# Include routers for modular endpoints
# app.include_router(book_router, prefix=f"{
#                    VERSION_PREFIX}/books", tags=["Books"])
# app.include_router(auth_router, prefix=f"{
#                    VERSION_PREFIX}/auth", tags=["Authentication"])
# app.include_router(review_router, prefix=f"{
#                    VERSION_PREFIX}/reviews", tags=["Reviews"])
# app.include_router(tags_router, prefix=f"{VERSION_PREFIX}/tags", tags=["Tags"])
