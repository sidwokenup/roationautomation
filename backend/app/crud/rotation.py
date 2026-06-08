from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timedelta

from app.db.models import RotationGroup, RotationLink, RotationHistory, RotationJob
from app.schemas.rotation import RotationGroupCreate, RotationGroupUpdate

class RotationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_group(self, group_in: RotationGroupCreate) -> RotationGroup:
        group = RotationGroup(
            campaign_id=group_in.campaign_id,
            name=group_in.name,
            interval_minutes=group_in.interval_minutes,
            is_active=False,
            is_paused=False,
            current_link_index=0
        )
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)

        for link_in in group_in.links:
            link = RotationLink(
                rotation_group_id=group.id,
                url=link_in.url,
                position=link_in.position,
                is_active=link_in.is_active
            )
            self.session.add(link)
        
        await self.session.commit()
        return await self.get_group(group.id)

    async def get_group(self, group_id: UUID) -> Optional[RotationGroup]:
        result = await self.session.execute(
            select(RotationGroup)
            .options(selectinload(RotationGroup.links)) # To fetch links together
            .where(RotationGroup.id == group_id)
        )
        return result.scalars().first()

    async def get_groups_by_campaign(self, campaign_id: UUID) -> List[RotationGroup]:
        result = await self.session.execute(
            select(RotationGroup)
            .options(selectinload(RotationGroup.links))
            .where(RotationGroup.campaign_id == campaign_id)
        )
        return result.scalars().all()

    async def list_groups(self) -> List[RotationGroup]:
        result = await self.session.execute(
            select(RotationGroup).options(selectinload(RotationGroup.links))
        )
        return result.scalars().all()

    async def update_group(self, group_id: UUID, update_data: RotationGroupUpdate) -> Optional[RotationGroup]:
        data = update_data.model_dump(exclude_unset=True)
        if data:
            await self.session.execute(
                update(RotationGroup)
                .where(RotationGroup.id == group_id)
                .values(**data)
            )
            await self.session.commit()
        return await self.get_group(group_id)

    async def update_group_index(self, group_id: UUID, index: int):
        await self.session.execute(
            update(RotationGroup).where(RotationGroup.id == group_id).values(current_link_index=index)
        )
        await self.session.commit()

    async def delete_group(self, group_id: UUID) -> bool:
        result = await self.session.execute(delete(RotationGroup).where(RotationGroup.id == group_id))
        await self.session.commit()
        return result.rowcount > 0

    async def log_history(self, group_id: UUID, campaign_id: UUID, previous_url: Optional[str], new_url: str, status: str, execution_time_ms: int = None, error_message: str = None):
        history = RotationHistory(
            rotation_group_id=group_id,
            campaign_id=campaign_id,
            previous_url=previous_url,
            new_url=new_url,
            rotation_status=status,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
        self.session.add(history)
        await self.session.commit()

    async def get_history(self, group_id: UUID, limit: int = 50) -> List[RotationHistory]:
        result = await self.session.execute(
            select(RotationHistory)
            .where(RotationHistory.rotation_group_id == group_id)
            .order_by(RotationHistory.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    # Job handling
    async def upsert_job(self, group_id: UUID, next_run_at: datetime, status: str = "scheduled"):
        result = await self.session.execute(select(RotationJob).where(RotationJob.rotation_group_id == group_id))
        job = result.scalars().first()
        if job:
            job.next_run_at = next_run_at
            job.status = status
            job.last_run_at = datetime.utcnow()
        else:
            job = RotationJob(
                rotation_group_id=group_id,
                next_run_at=next_run_at,
                status=status
            )
            self.session.add(job)
        await self.session.commit()

    async def get_overdue_jobs(self) -> List[RotationJob]:
        now = datetime.utcnow()
        result = await self.session.execute(
            select(RotationJob)
            .where(RotationJob.next_run_at <= now, RotationJob.status == "scheduled")
        )
        return result.scalars().all()
    
    async def get_job(self, group_id: UUID) -> Optional[RotationJob]:
        result = await self.session.execute(select(RotationJob).where(RotationJob.rotation_group_id == group_id))
        return result.scalars().first()

    async def update_job_status(self, job_id: UUID, status: str):
        await self.session.execute(
            update(RotationJob).where(RotationJob.id == job_id).values(status=status)
        )
        await self.session.commit()