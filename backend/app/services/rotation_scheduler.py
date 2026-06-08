import asyncio
import time
from uuid import UUID
from datetime import datetime, timedelta
import logging
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.db.models import RotationGroup, RotationJob
from app.crud.rotation import RotationRepository
from app.crud.campaign import CampaignRepository
from app.services.palladium_client import PalladiumClient
from app.core.tasks import TaskDispatcher

logger = logging.getLogger(__name__)

async def execute_rotation(group_id_str: str):
    start_time = time.time()
    group_id = UUID(group_id_str)
    
    async with AsyncSessionLocal() as session:
        rot_repo = RotationRepository(session)
        camp_repo = CampaignRepository(session)
        
        group = await rot_repo.get_group(group_id)
        if not group or not group.is_active or group.is_paused:
            logger.info(f"Rotation group {group_id} is not active or is paused. Skipping.")
            return

        campaign = await camp_repo.get_by_id(group.campaign_id)
        if not campaign:
            logger.error(f"Campaign {group.campaign_id} not found for rotation {group_id}")
            return

        active_links = [link for link in group.links if link.is_active]
        if not active_links:
            logger.warning(f"No active links for rotation {group_id}")
            return

        # Sort by position
        active_links.sort(key=lambda x: x.position)
        
        # Calculate next index
        next_index = (group.current_link_index + 1) % len(active_links)
        # If the current index was out of bounds, reset to 0
        if next_index >= len(active_links):
            next_index = 0
            
        new_link = active_links[next_index]
        previous_url = active_links[group.current_link_index].url if group.current_link_index < len(active_links) else None

        # Update Palladium API
        client = PalladiumClient()
        
        error_msg = None
        status = "SUCCESS"
        try:
            # Fetch existing campaign settings to preserve target_mode (e.g. Redirect vs iFrame)
            existing_res = await client.get_campaign(campaign.palladium_id)
            existing_data = existing_res.get("result", {})
            
            if existing_data and isinstance(existing_data, dict):
                payload = existing_data
                payload["campaign_id"] = campaign.palladium_id
                payload["target_link"] = new_link.url
                payload["target_mode"] = 2 # Force Redirect mode on rotation
            else:
                # Fallback if get_campaign doesn't return expected structure
                payload = {
                    "campaign_id": campaign.palladium_id,
                    "campaign_name": campaign.name,
                    "target_link": new_link.url,
                    "bot_link": campaign.bot_link or "bot.php",
                    "target_mode": 2, # Force Redirect mode
                    "target_link_logic": "default"
                }

            res = await client.update_campaign(payload)
            if not res.get("result", {}).get("success"):
                status = "FAILED"
                error_msg = "Palladium API returned success: false"
        except Exception as e:
            status = "FAILED"
            error_msg = str(e)
            logger.error(f"Rotation failed for {group_id}: {error_msg}")
        finally:
            await client.close()

        exec_time_ms = int((time.time() - start_time) * 1000)

        # Log history
        await rot_repo.log_history(
            group_id=group_id,
            campaign_id=campaign.id,
            previous_url=previous_url,
            new_url=new_link.url,
            status=status,
            execution_time_ms=exec_time_ms,
            error_message=error_msg
        )

        if status == "SUCCESS":
            # Update current index
            await rot_repo.update_group_index(group_id, next_index)
            # Also update the local campaign record
            from app.schemas.campaign import CampaignUpdate
            await camp_repo.update(campaign.id, CampaignUpdate(target_link=new_link.url))

        # Schedule next run regardless of success/failure (don't stop automatically)
        next_run_at = datetime.utcnow() + timedelta(minutes=group.interval_minutes)
        await rot_repo.upsert_job(group_id, next_run_at, "scheduled")

class RotationSchedulerService:
    @staticmethod
    async def dispatch_due_jobs():
        """Called periodically (e.g. by Celery beat) to dispatch due jobs"""
        # Avoid circular import
        from app.worker.tasks import rotate_campaign_link
        from app.db.session import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = RotationRepository(session)
            now = datetime.utcnow()
            
            # Find all jobs where next_run_at <= now and status != 'running'
            due_jobs = await repo.get_overdue_jobs()
            
            for job in due_jobs:
                # Update status to running
                await repo.upsert_job(job.rotation_group_id, job.next_run_at, "running")
                
                # Dispatch celery task
                TaskDispatcher.dispatch(rotate_campaign_link, str(job.rotation_group_id))

    @staticmethod
    async def recover_jobs():
        """Called on startup to recover jobs"""
        # Avoid circular import
        from app.worker.tasks import rotate_campaign_link
        from app.db.session import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            repo = RotationRepository(session)
            now = datetime.utcnow()
            
            # Find all active rotation groups
            groups_res = await session.execute(select(RotationGroup).where(RotationGroup.is_active == True, RotationGroup.is_paused == False))
            groups = groups_res.scalars().all()
            
            for group in groups:
                job_res = await session.execute(select(RotationJob).where(RotationJob.rotation_group_id == group.id))
                job = job_res.scalars().first()
                
                if not job or job.next_run_at <= now or job.status == 'running':
                    # Needs recovery
                    logger.info(f"Recovering rotation job for group {group.id}")
                    await repo.upsert_job(group.id, now, "scheduled")
                    TaskDispatcher.dispatch(rotate_campaign_link, str(group.id))