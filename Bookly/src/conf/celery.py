from celery import Celery
from .config import settings

# Initialize Celery instance
celery_app = Celery(
    "worker",
    # broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    # backend=f"redis://{settings.REDIS_HOST}:{
    #     settings.REDIS_PORT}/{settings.REDIS_DB}",
)

celery_app.conf.update(
    task_routes={
        'src.tasks.*': {'queue': 'default'},
    }
)


@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
