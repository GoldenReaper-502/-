from fastapi import APIRouter

from backend.storage.repository import repo

router = APIRouter(tags=['dev'])


@router.post('/dev/seed')
def seed_data():
    repo.seed()
    return {'ok': True, 'message': 'Seed completed'}


@router.post('/dev/reset')
def reset_data():
    repo.reset()
    return {'ok': True, 'message': 'Reset + seed completed'}
