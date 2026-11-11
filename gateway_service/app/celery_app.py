"""
celery_app.py

Celery application: connects the gateway to the Redis broker.
The same app is used by the gateway (to send tasks) and by the celery_worker (to run them).
"""

from celery import Celery
from config import settings

celery_app = Celery(
    "gateway",
    broker=settings.REDIS_URL,  # Redis keeps the queue of tasks
    include=["app.tasks"],  # modules with tasks that the worker has to load
)
