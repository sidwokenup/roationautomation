import asyncio
import logging
from typing import List, Dict
from uuid import UUID
from app.worker.celery_app import celery_app
from app.services.rotation_scheduler import execute_rotation, RotationSchedulerService
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

@celery_app.task(name="app.worker.tasks.dead_letter_task")
def dead_letter_task(task_id, task_name, args, kwargs, exception):
    logger.error(f"Task {task_name}[{task_id}] failed permanently: {exception}")

@celery_app.task(bind=True, name="app.worker.tasks.rotate_campaign_link", max_retries=3)
def rotate_campaign_link(self, group_id_str: str):
    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(execute_rotation(group_id_str))
    except Exception as exc:
        if hasattr(self.request, 'retries'):
            if self.request.retries >= self.max_retries:
                dead_letter_task.delay(self.request.id, self.name, self.request.args, self.request.kwargs, str(exc))
            countdown = 2 ** self.request.retries * 60
            raise self.retry(exc=exc, countdown=countdown)
        else:
            logger.error(f"Task rotate_campaign_link failed locally: {exc}")

@celery_app.task(name="app.worker.tasks.dispatch_rotations")
def dispatch_rotations():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(RotationSchedulerService.dispatch_due_jobs())

@celery_app.task(name="app.worker.tasks.recover_rotations")
def recover_rotations():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(RotationSchedulerService.recover_jobs())

# Setup periodic tasks (Celery Beat)
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from celery.schedules import crontab
    
    sender.add_periodic_task(60.0, dispatch_rotations.s(), name='dispatch every minute')
    sender.add_periodic_task(300.0, recover_rotations.s(), name='recover stuck rotations every 5 mins')