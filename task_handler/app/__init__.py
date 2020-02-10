import os
from celery import Celery
# from celery.app.registry import TaskRegistry
# from .diver_task import DiverTask

def make_celery(app_name=__name__):
    # registry = TaskRegistry()
    # registry.register(DiverTask())
    redis_host = os.environ.get('REDIS_URI', "redis://localhost:6379")
    backend = f"{redis_host}/0"
    broker = f"{redis_host}/1"
    # return Celery(app_name, backend=backend, broker=broker, tasks=registry)
    return Celery(app_name, backend=backend, broker=broker)

celery = make_celery()
