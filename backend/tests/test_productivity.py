import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.productivity import BulkOperationService
from app.db.models import User

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_bulk_update_campaigns(mock_db):
    service = BulkOperationService(mock_db)
    
    # Mock repository
    mock_op = AsyncMock()
    mock_op.id = uuid4()
    service.repo.create_operation = AsyncMock(return_value=mock_op)
    
    mock_user = User(id=uuid4())
    camp_ids = [uuid4(), uuid4()]
    
    with patch("app.services.productivity.celery_app.send_task") as mock_send_task:
        result = await service.bulk_update_campaigns(camp_ids, {"target_mode": 2}, mock_user)
        
        service.repo.create_operation.assert_called_once_with("update_campaigns", 2, mock_user.id)
        mock_send_task.assert_called_once_with(
            "app.worker.tasks.execute_bulk_operation",
            args=[str(mock_op.id), "update_campaigns", [str(i) for i in camp_ids], str(mock_user.id), {"target_mode": 2}]
        )
        assert result.id == mock_op.id

@pytest.mark.asyncio
async def test_bulk_start_rotations(mock_db):
    service = BulkOperationService(mock_db)
    
    mock_op = AsyncMock()
    mock_op.id = uuid4()
    service.repo.create_operation = AsyncMock(return_value=mock_op)
    
    mock_user = User(id=uuid4())
    rot_ids = [uuid4()]
    
    with patch("app.services.productivity.celery_app.send_task") as mock_send_task:
        result = await service.bulk_start_rotations(rot_ids, mock_user)
        
        service.repo.create_operation.assert_called_once_with("start_rotations", 1, mock_user.id)
        mock_send_task.assert_called_once()
        assert result.id == mock_op.id