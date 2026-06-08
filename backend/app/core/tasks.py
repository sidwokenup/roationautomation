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
        if settings.DEV_MODE:
            logger.info(f"[DEV_MODE] Executing task {celery_task.name} synchronously/in-memory")
            
            # Since some of our celery tasks (like process_bulk_operation) are async functions
            # wrapped in a synchronous celery task, we can just call the synchronous celery task
            # directly. The celery task itself already manages its own event loop if needed.
            # However, to avoid blocking the main thread for long operations in DEV_MODE, 
            # we can run it in a threadpool or asyncio task.
            
            # We will use asyncio.create_task if we are in an async context, or thread for sync.
            try:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, celery_task, *args, **kwargs)
            except RuntimeError:
                # No running loop, just execute
                celery_task(*args, **kwargs)
        else:
            celery_task.delay(*args, **kwargs)
