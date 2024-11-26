# celery_tasks.py
from celery import Celery
from .celery import celery_app


@celery_app.task
def send_email(to, subject, body):
    # Simulate sending an email task
    print(f"Sending email to {to} with subject {subject} and body {body}")
    return {"message": "Email sent successfully", "to": to}

