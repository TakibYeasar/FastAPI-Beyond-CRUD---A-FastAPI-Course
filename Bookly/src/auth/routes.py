from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.conf.database import get_db
from src.conf.redis import add_jti_to_blocklist
from src.conf.celery_tasks import send_email
from src.conf.config import settings
from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
)
from .schemas import (
    UserCreateModel,
    UserLoginModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .services import UserService
from .utils import (
    create_access_token,
    verify_password,
    generate_passwd_hash,
    create_url_safe_token,
    decode_url_safe_token,
)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY_DAYS = 2


@auth_router.post("/send_mail", summary="Send a welcome email")
async def send_mail(emails: EmailModel):
    """
    Send a welcome email to the provided email addresses.
    """
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    send_email.delay(emails.addresses, subject, html)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={
            "message": "Email sent successfully"}
    )


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, summary="User Signup")
async def create_user_account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new user account and send a verification email.
    """
    email = user_data.email
    if await user_service.user_exists(email, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
        )

    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    verification_link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify Your Email</h1>
    <p>Please click this <a href="{verification_link}">link</a> to verify your email</p>
    """
    send_email.delay([email], "Verify Your Email", html)

    return {
        "message": "Account created! Check your email to verify your account.",
        "user": new_user,
    }


@auth_router.get("/verify/{token}", summary="Verify User Account")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_db)):
    """
    Verify a user's email address using the provided token.
    """
    try:
        token_data = decode_url_safe_token(token)
        user_email = token_data.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: email not found.",
            )

        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Account verified successfully"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@auth_router.post("/login", summary="User Login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access and refresh tokens.
    """
    user = await user_service.get_user_by_email(login_data.email, session)
    if user and verify_password(login_data.password, user.password_hash):
        access_token = create_access_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": user.role,
            }
        )
        refresh_token = create_access_token(
            user_data={"email": user.email, "user_uid": str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"email": user.email, "uid": str(user.uid)},
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
    )


@auth_router.get("/refresh_token", summary="Refresh Access Token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Generate a new access token using a valid refresh token.
    """
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"access_token": new_access_token},
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired."
    )


@auth_router.get("/logout", summary="Logout User")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    """
    Revoke the current access token, logging the user out.
    """
    await add_jti_to_blocklist(token_details["jti"])
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={
            "message": "Logged out successfully"}
    )


@auth_router.post("/password-reset-request", summary="Request Password Reset")
async def password_reset_request(email_data: PasswordResetRequestModel):
    """
    Request a password reset for a user account.
    """
    token = create_url_safe_token({"email": email_data.email})
    reset_link = f"http://{settings.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html = f"""
    <h1>Reset Your Password</h1>
    <p>Click <a href="{reset_link}">here</a> to reset your password</p>
    """
    send_email.delay([email_data.email], "Reset Your Password", html)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset instructions sent to your email"},
    )


@auth_router.post("/password-reset-confirm/{token}", summary="Reset Password")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_db),
):
    """
    Reset the user's password using the provided token.
    """
    if passwords.new_password != passwords.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    try:
        token_data = decode_url_safe_token(token)
        user_email = token_data.get("email")
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        passwd_hash = generate_passwd_hash(passwords.new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Password reset successfully"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
