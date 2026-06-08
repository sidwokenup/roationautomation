from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class RotationLinkBase(BaseModel):
    url: str
    position: int
    is_active: bool = True

class RotationLinkCreate(RotationLinkBase):
    pass

class RotationLinkResponse(RotationLinkBase):
    id: UUID
    rotation_group_id: UUID
    created_at: datetime
    class Config:
        from_attributes = True

class RotationGroupBase(BaseModel):
    name: str
    interval_minutes: int
    campaign_id: UUID

class RotationGroupCreate(RotationGroupBase):
    links: List[RotationLinkCreate]

class RotationGroupUpdate(BaseModel):
    name: Optional[str] = None
    interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None

class RotationGroupResponse(RotationGroupBase):
    id: UUID
    is_active: bool
    is_paused: bool
    current_link_index: int
    created_at: datetime
    updated_at: datetime
    links: List[RotationLinkResponse] = []
    
    class Config:
        from_attributes = True

class RotationHistoryResponse(BaseModel):
    id: UUID
    rotation_group_id: UUID
    campaign_id: UUID
    previous_url: Optional[str] = None
    new_url: str
    rotation_status: str
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True