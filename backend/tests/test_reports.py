import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from app.services.report import ReportService
from app.services.export import ExportService

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_trigger_report_generation(mock_db):
    service = ReportService(mock_db)
    
    mock_report = AsyncMock()
    mock_report.id = uuid4()
    service.repo.create_report = AsyncMock(return_value=mock_report)
    
    with patch("app.services.report.celery_app.send_task") as mock_send_task:
        res = await service.trigger_report_generation("Test Report", "campaign", "csv", uuid4())
        
        service.repo.create_report.assert_called_once()
        mock_send_task.assert_called_once_with("app.worker.tasks.generate_report", args=[str(mock_report.id)])
        assert res.id == mock_report.id

def test_export_json():
    svc = ExportService()
    data = {"test": "data"}
    res = svc.export_json(data)
    assert b'"test": "data"' in res

def test_export_csv():
    svc = ExportService()
    data = {"campaigns": [{"name": "C1", "status": "active"}]}
    res = svc.export_csv(data)
    # Basic check for headers and data
    assert b'name,status' in res
    assert b'C1,active' in res

@pytest.mark.asyncio
async def test_execute_report(mock_db):
    service = ReportService(mock_db)
    
    mock_report = AsyncMock()
    mock_report.id = uuid4()
    mock_report.report_type = "campaign"
    mock_report.report_format = "json"
    mock_report.name = "Test JSON Report"
    
    service.repo.get_report = AsyncMock(return_value=mock_report)
    service.repo.update_report_status = AsyncMock()
    
    # Mock data gathering to bypass DB logic for unit test
    service._gather_data = AsyncMock(return_value={"campaigns": []})
    
    with patch("app.services.report.StorageService.upload_backup", new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = "mock/path.json"
        
        await service.execute_report(mock_report.id)
        
        service._gather_data.assert_called_once_with("campaign")
        mock_upload.assert_called_once()
        service.repo.update_report_status.assert_called_once_with(
            mock_report.id, "completed", file_path="mock/path.json", file_size=pytest.approx(33, abs=5) # length of json dump
        )