from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.core.errors import AppError
from backend.core.security import create_token, decode_token
from backend.storage.repository import repo

router = APIRouter(tags=['auth'])


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post('/auth/login')
def login(payload: LoginRequest):
    user = repo.find_user_credentials(payload.username, payload.password)
    if not user:
        raise AppError('Invalid credentials', 401)

    access = create_token({'user_id': user['id'], 'role': user['role'], 'company_id': user.get('company_id')}, 120)
    refresh = create_token({'user_id': user['id'], 'type': 'refresh'}, 1440)
    return {
        'access_token': access,
        'refresh_token': refresh,
        'token_type': 'bearer',
        'user': {k: v for k, v in user.items() if k != 'password'},
    }


@router.post('/auth/refresh')
def refresh_token(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if data.get('type') != 'refresh':
        raise AppError('Invalid refresh token', 401)
    user = repo.get_user(data.get('user_id'))
    if not user:
        raise AppError('User not found', 401)

    access = create_token({'user_id': user['id'], 'role': user['role'], 'company_id': user.get('company_id')}, 120)
    return {'access_token': access, 'token_type': 'bearer'}


@router.get('/auth/me')
def me(user: dict = Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != 'password'}


@router.get('/roles')
def roles(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    _ = tenant
    return repo.all('roles')


@router.get('/permissions')
def permissions(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    _ = tenant
    return repo.all('permissions')


@router.get('/users')
def users(company_id: str | None = None, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user, company_id)
    users_data = repo.list_tenant('users', tenant)
    return [{k: v for k, v in u.items() if k != 'password'} for u in users_data]
