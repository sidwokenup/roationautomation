from celery import Celery
from app.core.config import settings
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

if getattr(settings, "SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[CeleryIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.worker.tasks.rotate_campaign_link": "rotations",
    "app.worker.tasks.dead_letter_task": "dead_letter",
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)