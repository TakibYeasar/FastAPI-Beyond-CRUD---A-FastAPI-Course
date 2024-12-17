from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from typing import List
from pathlib import Path
from .config import Config

# Base directory for locating templates or other static resources
BASE_DIR = Path(__file__).resolve().parent

# Email Configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    # Uncomment and set the TEMPLATE_FOLDER when using email templates
    # TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)

# Initialize FastMail instance
mail = FastMail(config=mail_config)


def create_message(recipients: List[str], subject: str, body: str) -> MessageSchema:
    """
    Create an email message schema for FastMail.

    Args:
        recipients (List[str]): A list of email addresses to send the email to.
        subject (str): The subject of the email.
        body (str): The body of the email, supports HTML.

    Returns:
        MessageSchema: The constructed email message.

    Raises:
        ValueError: If recipients list is empty or invalid arguments are provided.
    """
    if not recipients:
        raise ValueError("The recipients list cannot be empty.")

    try:
        message = MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType.html,  # Specify HTML email subtype
        )
        return message
    except Exception as e:
        raise ValueError(f"Failed to create the email message: {e}")
