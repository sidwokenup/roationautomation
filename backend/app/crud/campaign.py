from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from uuid import UUID
from app.db.models import Campaign, CampaignTag, CampaignNote, CampaignActivityLog
from app.schemas.campaign import CampaignUpdate

class CampaignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        result = await self.session.execute(select(Campaign).where(Campaign.id == campaign_id))
        return result.scalars().first()

    async def get_by_palladium_id(self, palladium_id: int) -> Optional[Campaign]:
        result = await self.session.execute(select(Campaign).where(Campaign.palladium_id == palladium_id))
        return result.scalars().first()

    async def list_campaigns(self, skip: int = 0, limit: int = 100, search: str = None) -> List[Campaign]:
        query = select(Campaign)
        if search:
            query = query.where(Campaign.name.ilike(f"%{search}%"))
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, palladium_id: int, name: str, target_link: str, bot_link: str = None, target_mode: int = 2) -> Campaign:
        db_campaign = Campaign(
            palladium_id=palladium_id,
            name=name,
            target_link=target_link,
            bot_link=bot_link,
            target_mode=target_mode
        )
        self.session.add(db_campaign)
        await self.session.commit()
        await self.session.refresh(db_campaign)
        return db_campaign

    async def update(self, campaign_id: UUID, campaign_in: CampaignUpdate) -> Optional[Campaign]:
        update_data = campaign_in.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(campaign_id)
            
        await self.session.execute(
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(campaign_id)

    async def delete(self, campaign_id: UUID) -> bool:
        result = await self.session.execute(delete(Campaign).where(Campaign.id == campaign_id))
        await self.session.commit()
        return result.rowcount > 0

    async def log_activity(self, campaign_id: UUID, action: str, details: str = None, user_id: UUID = None):
        log = CampaignActivityLog(
            campaign_id=campaign_id,
            action=action,
            details=details,
            user_id=user_id
        )
        self.session.add(log)
        await self.session.commit()

    async def get_tags(self, campaign_id: UUID) -> List[str]:
        result = await self.session.execute(select(CampaignTag.tag).where(CampaignTag.campaign_id == campaign_id))
        return result.scalars().all()