from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.palladium_client import PalladiumClient
from app.crud.campaign import CampaignRepository

class CampaignSyncService:
    def __init__(self, db: AsyncSession):
        self.repo = CampaignRepository(db)
        self.client = PalladiumClient()
        self.db = db

    async def sync_all(self):
        try:
            # Note: The Palladium API uses getCampaignsList
            payload = {"page": 1, "limit": 1000}
            res = await self.client._post("/v1/campaign/getCampaignsList", payload)
            campaigns = res.get("result", {}).get("campaignsList", [])
            
            synced_count = 0
            for camp in campaigns:
                palladium_id = camp["id"]
                existing = await self.repo.get_by_palladium_id(palladium_id)
                if not existing:
                    # Create local copy
                    await self.repo.create(
                        palladium_id=palladium_id,
                        name=camp.get("name", "Unknown"),
                        target_link=camp.get("target_link", ""),
                        bot_link=camp.get("bot_link", ""),
                        target_mode=2 # Hardcode to Redirect
                    )
                    synced_count += 1
            
            return {"status": "success", "synced": synced_count, "total_remote": len(campaigns)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")