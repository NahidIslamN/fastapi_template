from celery import Celery
from core.config import REDIS_BROKER_URL, REDIS_BACKEND_URL

celery_app = Celery(
    "fastapi_celery",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
    include=["apps.auth.tasks"]
)

# autodiscover tasks from REAL packages
celery_app.autodiscover_tasks([
    "apps",
    "core",
])

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Dhaka",
    enable_utc=True,
)
