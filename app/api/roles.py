from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.api.deps import get_supabase_service, get_current_user_id
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get(
    "",
    summary="Получить все роли",
    description="Возвращает список всех доступных ролей в системе"
)
async def get_roles(
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить список всех доступных ролей.
    
    Возвращает массив ролей с их описанием, категорией и уровнем.
    """
    try:
        roles = await supabase_service.get_all_roles()
        return {"roles": roles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roles: {str(e)}")


@router.get(
    "/{role_id}/competencies",
    summary="Получить компетенции роли",
    description="Возвращает список компетенций, которые тестируются для указанной роли"
)
async def get_role_competencies(
    role_id: UUID = ..., description="ID роли",
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Получить компетенции для указанной роли.
    
    Возвращает упорядоченный список компетенций с их описанием, важностью и категорией.
    Компетенции отсортированы по order_index.
    """
    try:
        competencies = await supabase_service.get_role_competencies(str(role_id))
        return {"competencies": competencies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching competencies: {str(e)}")
