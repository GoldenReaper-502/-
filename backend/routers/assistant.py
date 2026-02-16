from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user

router = APIRouter(tags=['assistant'])


class AssistantQuery(BaseModel):
    query: str
    context: dict | None = None


@router.post('/assistant/query')
def assistant_query(payload: AssistantQuery, user: dict = Depends(get_current_user)):
    return {
        'response': f"[Mock AI] Suggested action for '{payload.query}': review incidents and permits in your site.",
        'todo': 'Integrate with LLM provider',
        'user_role': user.get('role'),
    }
