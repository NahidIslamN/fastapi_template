import sys
import os
from celery import Celery
from core.config import REDIS_BROKER_URL, REDIS_BACKEND_URL

# ✅ FORCE project root into PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

celery_app = Celery(
    "fastapi_celery",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Dhaka",
    enable_utc=True,
)

import apps.auth.tasks  