from fastapi import APIRouter, Depends

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import repo

router = APIRouter(tags=['companies'])


@router.get('/companies')
def companies(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('companies', tenant)


@router.get('/sites')
def sites(company_id: str | None = None, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user, company_id)
    return repo.list_tenant('sites', tenant)


@router.get('/departments')
def departments(company_id: str | None = None, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user, company_id)
    return repo.list_tenant('departments', tenant)
