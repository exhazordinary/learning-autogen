"""Celery application configuration."""

from celery import Celery
import os


def make_celery(app_name: str = 'autogen_research'):
    """Create and configure Celery application."""
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
        include=['src.autogen_research.tasks.research_tasks']
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=600,  # 10 minutes
        task_soft_time_limit=540,  # 9 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=50,
    )

    return celery


celery_app = make_celery()
