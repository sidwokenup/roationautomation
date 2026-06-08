from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time

from app.crud.rotation import RotationRepository
from app.crud.campaign import CampaignRepository
from app.schemas.rotation import RotationGroupCreate, RotationGroupUpdate
from app.services.palladium_client import PalladiumClient
from app.core.tasks import TaskDispatcher
from app.worker.tasks import rotate_campaign_link

class RotationService:
    def __init__(self, db: AsyncSession):
        self.repo = RotationRepository(db)
        self.campaign_repo = CampaignRepository(db)
        self.client = PalladiumClient()

    async def create_group(self, group_in: RotationGroupCreate):
        campaign = await self.campaign_repo.get_by_id(group_in.campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return await self.repo.create_group(group_in)

    async def update_group(self, group_id: UUID, update_data: RotationGroupUpdate):
        return await self.repo.update_group(group_id, update_data)

    async def delete_group(self, group_id: UUID):
        await self.stop_rotation(group_id) # Ensure job is stopped
        return await self.repo.delete_group(group_id)

    async def get_group(self, group_id: UUID):
        group = await self.repo.get_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Rotation group not found")
        return group

    async def list_groups(self):
        return await self.repo.list_groups()

    async def start_rotation(self, group_id: UUID):
        group = await self.get_group(group_id)
        if group.is_active and not group.is_paused:
            return group # Already running

        await self.repo.update_group(group_id, RotationGroupUpdate(is_active=True, is_paused=False))
        
        # Schedule the first run immediately or set next_run_at
        next_run = datetime.utcnow()
        await self.repo.upsert_job(group_id, next_run, "scheduled")
        
        # Trigger celery task asynchronously
        TaskDispatcher.dispatch(rotate_campaign_link, str(group_id))
        return await self.get_group(group_id)

    async def pause_rotation(self, group_id: UUID):
        group = await self.get_group(group_id)
        await self.repo.update_group(group_id, RotationGroupUpdate(is_paused=True))
        
        job = await self.repo.get_job(group_id)
        if job:
            await self.repo.update_job_status(job.id, "paused")
        return await self.get_group(group_id)

    async def resume_rotation(self, group_id: UUID):
        group = await self.get_group(group_id)
        if not group.is_active:
            raise HTTPException(status_code=400, detail="Cannot resume an inactive rotation. Start it first.")
        
        await self.repo.update_group(group_id, RotationGroupUpdate(is_paused=False))
        next_run = datetime.utcnow()
        await self.repo.upsert_job(group_id, next_run, "scheduled")
        TaskDispatcher.dispatch(rotate_campaign_link, str(group_id))
        return await self.get_group(group_id)

    async def stop_rotation(self, group_id: UUID):
        await self.repo.update_group(group_id, RotationGroupUpdate(is_active=False, is_paused=False))
        job = await self.repo.get_job(group_id)
        if job:
            await self.repo.update_job_status(job.id, "stopped")
        return await self.get_group(group_id)

    async def rotate_now(self, group_id: UUID):
        # Trigger immediately without changing schedule
        TaskDispatcher.dispatch(rotate_campaign_link, str(group_id))
        return {"status": "Rotation task queued"}

    async def get_history(self, group_id: UUID):
        return await self.repo.get_history(group_id)