from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from uuid import UUID
from app.db.models import CampaignStatus

class CampaignBase(BaseModel):
    name: str
    target_link: str
    bot_link: Optional[str] = None
    target_mode: int = 2
    status: CampaignStatus = CampaignStatus.ACTIVE

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    target_link: Optional[str] = None
    bot_link: Optional[str] = None
    target_mode: Optional[int] = None
    status: Optional[CampaignStatus] = None

class CampaignInDB(CampaignBase):
    id: UUID
    palladium_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignResponse(CampaignInDB):
    tags: List[str] = []
