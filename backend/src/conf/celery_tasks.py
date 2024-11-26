from .celery import celery_app
from .utils import mail, create_message
from asgiref.sync import async_to_sync
from typing import List


@celery_app.task()
def send_email(recipients: List[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)

    # Ensure `mail.send_message` is async; otherwise, this conversion is unnecessary
    async_to_sync(mail.send_message)(message)
    print("Email sent")
