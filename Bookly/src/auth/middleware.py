import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Configure logger
logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.INFO)  # Enable logging only for relevant levels


def register_middleware(app: FastAPI):
    """Registers custom and built-in middleware for the FastAPI app."""

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        """Middleware to log request details and processing time."""
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate the processing time
        processing_time = time.time() - start_time

        # Log the details
        logger.info(
            "%s:%s - %s %s - Status %d - Completed in %.4fs",
            request.client.host,
            # Handle cases where port might not be available
            request.client.port or "unknown",
            request.method,
            request.url.path,
            response.status_code,
            processing_time,
        )
        return response

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update to specific domains for production
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Add Trusted Host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "bookly-api-dc03.onrender.com",
            "0.0.0.0",
        ],  # Consider using an environment variable for flexibility
    )
