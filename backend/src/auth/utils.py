import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from src.conf.config import Config

# Initialize password hashing context
passwd_context = CryptContext(schemes=["bcrypt"])

# Constants
ACCESS_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour


def generate_password_hash(password: str) -> str:
    """
    Generate a hashed version of the provided password.
    """
    return passwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify if the provided password matches the hashed password.
    """
    return passwd_context.verify(password, hashed_password)


def create_access_token(
    user_data: Dict[str, str],
    expiry: Optional[timedelta] = None,
    refresh: bool = False,
) -> str:
    """
    Create a JWT access token for a user.
    """
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry or timedelta(seconds=ACCESS_TOKEN_EXPIRY_SECONDS)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    return jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token to retrieve its payload.
    """
    try:
        return jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired.")
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")
    except Exception as e:
        logging.exception(f"Unexpected error while decoding token: {e}")

    return None


# Initialize serializer for generating URL-safe tokens
serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET,
    salt="email-configuration",
)


def create_url_safe_token(data: Dict[str, str]) -> str:
    """
    Create a URL-safe token using the provided data.
    """
    return serializer.dumps(data)


def decode_url_safe_token(token: str) -> Optional[Dict[str, str]]:
    """
    Decode a URL-safe token to retrieve its data.
    """
    try:
        return serializer.loads(token)
    except Exception as e:
        logging.error(f"Error decoding URL-safe token: {e}")

    return None
