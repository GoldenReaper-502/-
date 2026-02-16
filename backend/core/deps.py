from __future__ import annotations

from typing import Callable

from fastapi import Header

from backend.core.errors import AppError
from backend.core.security import decode_token
from backend.storage.repository import repo


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith('bearer '):
        raise AppError('Missing bearer token', 401)

    token = authorization.split(' ', 1)[1]
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise AppError(str(exc), 401)

    user = repo.get_user(payload.get('user_id'))
    if not user:
        raise AppError('User not found', 401)
    return user


def require_roles(*allowed: str) -> Callable:
    def checker(user: dict) -> dict:
        if user.get('role') not in allowed:
            raise AppError('Forbidden', 403)
        return user

    return checker


def get_tenant_scope(user: dict, company_id: str | None = None) -> str | None:
    if user.get('role') == 'SuperAdmin':
        return company_id
    return user.get('company_id')
