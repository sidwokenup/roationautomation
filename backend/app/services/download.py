import io
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.services.palladium_client import PalladiumClient
from app.crud.campaign import CampaignRepository
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

class DownloadService:
    def __init__(self, db: AsyncSession):
        self.repo = CampaignRepository(db)
        self.client = PalladiumClient()

    async def _download(self, campaign_id: UUID, endpoint_suffix: str):
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        url = f"{self.client.base_url}/v1/company/{endpoint_suffix}"
        try:
            res = await self.client.client.get(url, params={"company": campaign.palladium_id})
            res.raise_for_status()
            
            # Use an async generator to stream the content properly for FastAPI StreamingResponse
            async def iterfile():
                yield res.content

            # Return as a stream
            return StreamingResponse(
                iterfile(),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=campaign_{campaign.palladium_id}_{endpoint_suffix}.zip"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

    async def download_zip(self, campaign_id: UUID):
        return await self._download(campaign_id, "download")

    async def download_wp(self, campaign_id: UUID):
        return await self._download(campaign_id, "downloadWp")