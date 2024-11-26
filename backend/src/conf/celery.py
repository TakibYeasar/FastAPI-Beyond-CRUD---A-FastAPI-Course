# celery.py
from celery import Celery
from .config import Config

# Initialize Celery instance
celery_app = Celery(
    "worker",  # Name of the worker
    # Redis connection URL
    broker=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}",
    # Optional result backend
    backend=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}",
)

celery_app.conf.update(
    task_routes={
        # Example of routing tasks to different queues
        'src.celery_tasks.*': {'queue': 'default'},
    }
)


@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
