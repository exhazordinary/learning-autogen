"""Celery tasks for async research processing."""

from .celery_app import celery_app
from .research_tasks import process_research_task

__all__ = ['celery_app', 'process_research_task']
