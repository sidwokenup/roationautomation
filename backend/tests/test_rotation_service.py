import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
import asyncio

from app.services.rotation import RotationService
from app.schemas.rotation import RotationGroupCreate, RotationLinkCreate, RotationGroupUpdate

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def rotation_service(mock_db):
    service = RotationService(mock_db)
    service.repo = AsyncMock()
    service.campaign_repo = AsyncMock()
    service.client = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_create_rotation_group(rotation_service):
    campaign_id = uuid4()
    group_in = RotationGroupCreate(
        name="Test Rotation",
        interval_minutes=15,
        campaign_id=campaign_id,
        links=[
            RotationLinkCreate(url="https://test1.com", position=0),
            RotationLinkCreate(url="https://test2.com", position=1)
        ]
    )

    rotation_service.campaign_repo.get_by_id.return_value = True
    rotation_service.repo.create_group.return_value = {"id": uuid4()}

    result = await rotation_service.create_group(group_in)
    
    rotation_service.campaign_repo.get_by_id.assert_called_once_with(campaign_id)
    rotation_service.repo.create_group.assert_called_once_with(group_in)
    assert result is not None

@pytest.mark.asyncio
async def test_start_rotation(rotation_service):
    group_id = uuid4()
    mock_group = AsyncMock()
    mock_group.is_active = False
    mock_group.is_paused = False
    
    rotation_service.get_group = AsyncMock(return_value=mock_group)
    rotation_service.repo.update_group = AsyncMock()
    rotation_service.repo.upsert_job = AsyncMock()

    with patch('app.services.rotation.celery_app.send_task') as mock_send_task:
        await rotation_service.start_rotation(group_id)
        
        rotation_service.repo.update_group.assert_called_once()
        rotation_service.repo.upsert_job.assert_called_once()
        mock_send_task.assert_called_once_with("app.worker.tasks.rotate_campaign_link", args=[str(group_id)])

@pytest.mark.asyncio
async def test_pause_rotation(rotation_service):
    group_id = uuid4()
    mock_job = AsyncMock()
    mock_job.id = uuid4()
    
    rotation_service.get_group = AsyncMock()
    rotation_service.repo.update_group = AsyncMock()
    rotation_service.repo.get_job = AsyncMock(return_value=mock_job)
    rotation_service.repo.update_job_status = AsyncMock()

    await rotation_service.pause_rotation(group_id)
    
    rotation_service.repo.update_group.assert_called_once()
    rotation_service.repo.update_job_status.assert_called_once_with(mock_job.id, "paused")

@pytest.mark.asyncio
async def test_stop_rotation(rotation_service):
    group_id = uuid4()
    mock_job = AsyncMock()
    mock_job.id = uuid4()
    
    rotation_service.repo.update_group = AsyncMock()
    rotation_service.repo.get_job = AsyncMock(return_value=mock_job)
    rotation_service.repo.update_job_status = AsyncMock()
    rotation_service.get_group = AsyncMock()

    await rotation_service.stop_rotation(group_id)
    
    rotation_service.repo.update_group.assert_called_once()
    rotation_service.repo.update_job_status.assert_called_once_with(mock_job.id, "stopped")