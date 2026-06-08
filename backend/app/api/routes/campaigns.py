from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.models import User
from app.schemas.campaign import CampaignUpdate, CampaignResponse
from app.services.campaign import CampaignService
from app.services.sync import CampaignSyncService
from app.services.download import DownloadService

router = APIRouter()

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = CampaignService(db)
    return await svc.list_campaigns(skip, limit, search)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = CampaignService(db)
    return await svc.get_campaign(campaign_id)

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_in: CampaignUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = CampaignService(db)
    return await svc.update_campaign(campaign_id, campaign_in, current_user)

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = CampaignService(db)
    success = await svc.delete_campaign(campaign_id, current_user)
    return {"status": "success" if success else "failed"}

@router.post("/sync")
async def sync_campaigns(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = CampaignSyncService(db)
    return await svc.sync_all()

@router.get("/{campaign_id}/download")
async def download_zip(
    campaign_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = DownloadService(db)
    return await svc.download_zip(campaign_id)

@router.get("/{campaign_id}/downloadWp")
async def download_wp(
    campaign_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = DownloadService(db)
    return await svc.download_wp(campaign_id)