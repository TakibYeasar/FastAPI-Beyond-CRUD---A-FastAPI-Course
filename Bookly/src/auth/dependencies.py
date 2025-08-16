from typing import Any, List, Optional
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from conf.database import get_db
from .models import User
from conf.redis import token_in_blocklist
from .services import AuthService
from .utils import decode_token

auth_service = AuthService()


class TokenBearer(HTTPBearer):
    """
    Base class for handling token authentication using HTTP Bearer.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        """
        Extract and validate token from the request.
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization credentials missing.",
            )

        token = credentials.credentials
        token_data = decode_token(token)

        if not self.token_valid(token_data):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data.",
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is revoked.",
            )

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token_data: Optional[dict]) -> bool:
        """
        Check if the token data is valid.
        """
        return token_data is not None

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify token data. Must be implemented in derived classes.
        """
        raise NotImplementedError(
            "Please implement this method in child classes."
        )


class AccessTokenBearer(TokenBearer):
    """
    Bearer token validator for access tokens.
    """

    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token cannot contain a refresh claim.",
            )


class RefreshTokenBearer(TokenBearer):
    """
    Bearer token validator for refresh tokens.
    """

    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token must contain a refresh claim.",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Retrieve the current authenticated user based on the access token.
    """
    user_email = token_details["user"]["email"]

    user = await auth_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


class RoleChecker:
    """
    Dependency to check if the current user has the required role(s).
    """

    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        """
        Ensure the current user is verified and has an allowed role.
        """
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not verified.",
            )

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required role.",
            )

        return True

