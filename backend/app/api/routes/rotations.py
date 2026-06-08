from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.models import User
from app.schemas.rotation import (
    RotationGroupCreate, 
    RotationGroupUpdate, 
    RotationGroupResponse,
    RotationHistoryResponse
)
from app.services.rotation import RotationService

router = APIRouter()

@router.get("/groups", response_model=List[RotationGroupResponse])
async def list_groups(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.list_groups()

@router.post("/groups", response_model=RotationGroupResponse)
async def create_group(
    group_in: RotationGroupCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.create_group(group_in)

@router.get("/groups/{id}", response_model=RotationGroupResponse)
async def get_group(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.get_group(id)

@router.put("/groups/{id}", response_model=RotationGroupResponse)
async def update_group(
    id: UUID,
    group_in: RotationGroupUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.update_group(id, group_in)

@router.delete("/groups/{id}")
async def delete_group(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    success = await svc.delete_group(id)
    return {"status": "success" if success else "failed"}

# Actions
@router.post("/groups/{id}/start", response_model=RotationGroupResponse)
async def start_rotation(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.start_rotation(id)

@router.post("/groups/{id}/pause", response_model=RotationGroupResponse)
async def pause_rotation(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.pause_rotation(id)

@router.post("/groups/{id}/resume", response_model=RotationGroupResponse)
async def resume_rotation(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.resume_rotation(id)

@router.post("/groups/{id}/stop", response_model=RotationGroupResponse)
async def stop_rotation(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.stop_rotation(id)

@router.post("/groups/{id}/rotate-now")
async def rotate_now(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.rotate_now(id)

@router.get("/groups/{id}/history", response_model=List[RotationHistoryResponse])
async def get_history(
    id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    svc = RotationService(db)
    return await svc.get_history(id)