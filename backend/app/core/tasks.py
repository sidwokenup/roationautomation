import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TaskDispatcher:
    """
    A unified dispatcher for executing background tasks.
    In DEV_MODE, it executes the task synchronously or as an asyncio background task to avoid requiring Celery/Redis.
    In Production, it routes the task to Celery using .delay() or .apply_async().
    """
    
    @staticmethod
    def dispatch(celery_task, *args, **kwargs):
        # We force in-memory execution because we do not have a Redis/Celery worker deployed
        logger.info(f"Executing task {celery_task.name} synchronously/in-memory")
        
        try:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, celery_task, *args, **kwargs)
        except RuntimeError:
            # No running loop, just execute
            celery_task(*args, **kwargs)
