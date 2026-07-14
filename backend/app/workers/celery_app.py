"""Celery application configuration."""
from __future__ import annotations

from celery import Celery
from app.config import settings

app = Celery(
    "rideverse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL.replace("/0", "/1"),
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=275,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

app.autodiscover_tasks(["app.workers"])
