from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging
from app.api.deps import get_supabase_service
from app.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get(
    "/directions",
    summary="Получить каталог направлений",
    description="Возвращает список всех доступных направлений разработки с опциональными вложенными технологиями"
)
async def get_directions_catalog(
    include_technologies: bool = Query(True, description="Включить список технологий для каждого направления"),
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """
    Получить каталог направлений с вложенными технологиями.
    
    Оптимизированный endpoint - один запрос вместо N+1.
    
    Args:
        include_technologies: если True, включает список технологий для каждого направления
    
    Returns:
        {
            "directions": [
                {
                    "id": "uuid",
                    "name": "frontend",
                    "display_name": "Frontend",
                    "description": "...",
                    "technologies": [  // если include_technologies=true
                        {"id": "uuid", "name": "react", "description": "..."}
                    ]
                }
            ]
        }
    """
    try:
        directions = await supabase_service.get_all_directions()
        
        if include_technologies:
            for direction in directions:
                try:
                    techs = await supabase_service.get_direction_technologies(direction['id'])
                    direction['technologies'] = [
                        {
                            'id': t['technologies']['id'],
                            'name': t['technologies']['name'],
                            'description': t['technologies'].get('description'),
                            'order_index': t.get('order_index')
                        }
                        for t in techs if t.get('technologies')
                    ]
                except Exception as e:
                    logger.warning(f"Could not fetch technologies for direction {direction['id']}: {e}")
                    direction['technologies'] = []
        
        return {"directions": directions}
    except Exception as e:
        logger.error(f"Error fetching directions catalog: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching directions catalog: {str(e)}")


@router.get(
    "/technologies/{technology_id}",
    summary="Получить детали технологии",
    description="Возвращает информацию о технологии"
)
async def get_technology(
    technology_id: UUID,
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """Получить детали технологии"""
    try:
        technology = await supabase_service.get_technology(str(technology_id))
        if not technology:
            raise HTTPException(status_code=404, detail="Technology not found")
        
        return {"technology": technology}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching technology: {str(e)}")


@router.get(
    "/roles",
    summary="Получить список ролей (deprecated)",
    description="DEPRECATED: Используйте directions и technologies вместо roles. Endpoint оставлен для обратной совместимости."
)
async def get_roles_catalog(
    supabase_service: SupabaseService = Depends(get_supabase_service)
):
    """
    Получить список ролей.
    
    ⚠️ DEPRECATED: Этот endpoint оставлен для обратной совместимости.
    Рекомендуется использовать /api/catalog/directions вместо этого.
    """
    try:
        roles = await supabase_service.get_all_roles()
        return {
            "roles": roles,
            "deprecated": True,
            "message": "This endpoint is deprecated. Please use /api/catalog/directions instead."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roles: {str(e)}")
