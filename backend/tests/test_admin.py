import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime

from app.services.admin import OrganizationService, RoleService, PermissionService, ApiKeyService, AuditLogService
from app.db.models import Organization, Role, Permission, ApiKey, AuditLog, User, OrganizationUser

@pytest.fixture
def mock_db_session(mocker):
    session = mocker.AsyncMock()
    return session

@pytest.mark.asyncio
async def test_organization_service_create_and_get(mock_db_session, mocker):
    svc = OrganizationService(mock_db_session)
    
    org_id = uuid4()
    mock_org = Organization(id=org_id, name="Test Org")
    
    mock_result = mocker.MagicMock()
    mock_result.scalars().first.return_value = mock_org
    mock_db_session.execute.return_value = mock_result
    
    org = await svc.get_organization(org_id)
    assert org is not None
    assert org.name == "Test Org"
    assert org.id == org_id

@pytest.mark.asyncio
async def test_organization_service_update(mock_db_session, mocker):
    svc = OrganizationService(mock_db_session)
    
    org_id = uuid4()
    mock_org = Organization(id=org_id, name="Updated Org")
    
    mock_result = mocker.MagicMock()
    mock_result.scalars().first.return_value = mock_org
    mock_db_session.execute.return_value = mock_result
    
    org = await svc.update_organization(org_id, "Updated Org")
    mock_db_session.commit.assert_called_once()
    assert org.name == "Updated Org"

@pytest.mark.asyncio
async def test_role_service_list_roles(mock_db_session, mocker):
    svc = RoleService(mock_db_session)
    
    org_id = uuid4()
    role1 = Role(id=uuid4(), organization_id=org_id, name="Admin")
    role2 = Role(id=uuid4(), organization_id=org_id, name="Viewer")
    
    mock_result = mocker.MagicMock()
    mock_result.scalars().all.return_value = [role1, role2]
    mock_db_session.execute.return_value = mock_result
    
    roles = await svc.list_roles(org_id)
    assert len(roles) == 2
    assert roles[0].name == "Admin"
    assert roles[1].name == "Viewer"

@pytest.mark.asyncio
async def test_api_key_service_create_key(mock_db_session):
    svc = ApiKeyService(mock_db_session)
    
    org_id = uuid4()
    api_key, raw_key = await svc.create_key(org_id, "Test Key")
    
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    
    assert raw_key.startswith("pk_")
    assert api_key.name == "Test Key"
    assert api_key.organization_id == org_id
    assert api_key.key_hash == svc._hash_key(raw_key)

@pytest.mark.asyncio
async def test_audit_log_service_log_action(mock_db_session):
    svc = AuditLogService(mock_db_session)
    
    user_id = uuid4()
    await svc.log_action(user_id, "campaign:create", "Campaign", "camp_123", {"name": "Test"})
    
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    
    added_log = mock_db_session.add.call_args[0][0]
    assert added_log.user_id == user_id
    assert added_log.action == "campaign:create"
    assert added_log.entity_type == "Campaign"
    assert added_log.entity_id == "camp_123"
    assert added_log.metadata_json == {"name": "Test"}
