import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # JWT_SECRET: str = os.getenv("JWT_SECRET")
    # JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    # REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    # MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    # MAIL_FROM: str = os.getenv("MAIL_FROM")
    # # Default to 587 if not provided
    # MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    # MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    # MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    # MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True") == "True"
    # MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False") == "True"
    # USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "True") == "True"
    # VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS", "True") == "True"
    DOMAIN: str = os.getenv("DOMAIN")


# Initialize settings instance
settings = Settings()

