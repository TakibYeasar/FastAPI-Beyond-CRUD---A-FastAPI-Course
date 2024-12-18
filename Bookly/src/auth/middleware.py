import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Configure logger
logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.INFO)  # Enable logging for relevant levels


def register_middleware(app: FastAPI):
    """
    Register custom and built-in middleware for the FastAPI app.

    Includes:
    - Custom logging middleware for request processing.
    - CORS middleware to handle cross-origin requests.
    - Trusted Host middleware to limit allowed hosts.
    """

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        """
        Custom middleware to log request details, status, and processing time.
        """
        start_time = time.time()

        try:
            # Process the request and get the response
            response = await call_next(request)
        except Exception as exc:
            # Handle unexpected exceptions and log error details
            logger.error(
                "Error processing request: %s %s - Error: %s",
                request.method,
                request.url.path,
                str(exc),
            )
            raise

        # Calculate the processing time
        processing_time = time.time() - start_time

        # Log request details
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
        # Allow all origins for development; restrict for production
        allow_origins=["*"],
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
        allow_credentials=True,  # Allow credentials such as cookies
    )

    # Add Trusted Host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",  # Local development
            "127.0.0.1",  # Localhost loopback
            "bookly-api-dc03.onrender.com",  # Example production domain
            # Bind-all IP address (e.g., containerized environments)
            "0.0.0.0",
        ],  # Use environment variables for flexibility in production
    )
