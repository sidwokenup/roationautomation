from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.campaign import CampaignRepository
from app.schemas.campaign import CampaignUpdate
from app.services.palladium_client import PalladiumClient
from app.db.models import User

class CampaignService:
    def __init__(self, db: AsyncSession):
        self.repo = CampaignRepository(db)
        self.client = PalladiumClient()

    async def update_campaign(self, campaign_id: UUID, campaign_in: CampaignUpdate, user: User):
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Force target_mode to 2 (Redirect) as requested
        target_mode = 2
        
        # 1. Update in Palladium
        try:
            existing_res = await self.client.get_campaign(campaign.palladium_id)
            existing_data = existing_res.get("result", {})
            
            if existing_data and isinstance(existing_data, dict):
                payload = existing_data
                payload["campaign_id"] = campaign.palladium_id
                if campaign_in.name:
                    payload["campaign_name"] = campaign_in.name
                if campaign_in.target_link:
                    payload["target_link"] = campaign_in.target_link
                if campaign_in.bot_link:
                    payload["bot_link"] = campaign_in.bot_link
                payload["target_mode"] = target_mode
            else:
                payload = {
                    "campaign_id": campaign.palladium_id,
                    "campaign_name": campaign_in.name or campaign.name,
                    "target_link": campaign_in.target_link or campaign.target_link,
                    "bot_link": campaign_in.bot_link or campaign.bot_link,
                    "target_mode": target_mode,
                    "target_link_logic": "default"
                }
            
            res = await self.client.update_campaign(payload)
            if not res.get("result", {}).get("success"):
                raise HTTPException(status_code=400, detail="Failed to update campaign in Palladium API")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # 2. Update local DB
        campaign_in.target_mode = target_mode
        updated_campaign = await self.repo.update(campaign_id, campaign_in)
        
        # 3. Log
        await self.repo.log_activity(campaign_id, "UPDATED", "Updated campaign fields", user.id)
        return updated_campaign

    async def delete_campaign(self, campaign_id: UUID, user: User):
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # 1. Delete in Palladium (optional if we just want to hide locally, but requirements imply full delete)
        try:
            # The client needs a delete_campaign method
            url = f"{self.client.base_url}/v1/campaign/deleteCampaign"
            res = await self.client.client.post(url, json={"campaignId": campaign.palladium_id})
            res.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete in Palladium: {str(e)}")

        # 2. Delete locally
        success = await self.repo.delete(campaign_id)
        return success

    async def get_campaign(self, campaign_id: UUID):
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

    async def list_campaigns(self, skip: int = 0, limit: int = 100, search: str = None):
        return await self.repo.list_campaigns(skip, limit, search)