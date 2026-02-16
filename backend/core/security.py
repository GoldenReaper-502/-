from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from backend.core.config import settings


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def _unb64(value: str) -> bytes:
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_token(payload: dict[str, Any], expires_minutes: int | None = None) -> str:
    body = payload.copy()
    body['exp'] = int(time.time()) + 60 * (expires_minutes or settings.access_token_minutes)
    raw = json.dumps(body, separators=(',', ':'), sort_keys=True).encode()
    sig = hmac.new(settings.secret_key.encode(), raw, hashlib.sha256).hexdigest().encode()
    return f"{_b64(raw)}.{_b64(sig)}"


def decode_token(token: str) -> dict[str, Any]:
    try:
        part_payload, part_sig = token.split('.')
        raw = _unb64(part_payload)
        sig = _unb64(part_sig).decode()
    except Exception as exc:
        raise ValueError('Invalid token format') from exc

    expected = hmac.new(settings.secret_key.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError('Invalid token signature')

    payload = json.loads(raw.decode())
    if payload.get('exp', 0) < int(time.time()):
        raise ValueError('Token expired')
    return payload
