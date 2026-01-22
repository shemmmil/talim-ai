from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.api.deps import get_supabase_service, get_current_user_id
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/admin", tags=["admin"])


# === SCHEMAS ===

class DirectionCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    technologies: Optional[str] = None
    description: Optional[str] = None


class TechnologyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DirectionTechnologyLink(BaseModel):
    direction_id: UUID
    technology_id: UUID
    order_index: Optional[int] = None


class TechnologyCompetencyLink(BaseModel):
    technology_id: UUID
    competency_id: UUID
    order_index: Optional[int] = None


class DirectionCompetencyLink(BaseModel):
    direction_id: UUID
    competency_id: UUID
    order_index: Optional[int] = None


class BatchTechnologyLink(BaseModel):
    technology_ids: List[UUID]


# === DIRECTIONS ===

@router.post(
    "/directions",
    summary="Создать направление",
    description="Создает новое направление разработки"
)
async def create_direction(
    direction_data: DirectionCreate,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Создать новое направление"""
    try:
        direction = await supabase_service.find_or_create_direction(
            name=direction_data.name,
            display_name=direction_data.display_name or direction_data.name,
            technologies=direction_data.technologies,
            description=direction_data.description
        )
        return {"direction": direction, "message": "Direction created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating direction: {str(e)}")


# === TECHNOLOGIES ===

@router.post(
    "/technologies",
    summary="Создать технологию",
    description="Создает новую технологию"
)
async def create_technology(
    technology_data: TechnologyCreate,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Создать новую технологию"""
    try:
        technology = await supabase_service.find_or_create_technology(
            name=technology_data.name,
            description=technology_data.description
        )
        return {"technology": technology, "message": "Technology created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating technology: {str(e)}")


@router.post(
    "/directions/{direction_id}/technologies/{technology_id}",
    summary="Связать технологию с направлением",
    description="Добавляет технологию к направлению"
)
async def link_technology_to_direction(
    direction_id: UUID,
    technology_id: UUID,
    order_index: Optional[int] = None,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Связать технологию с направлением"""
    try:
        # Проверяем существование направления
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        # Проверяем существование технологии
        technology = await supabase_service.get_technology(str(technology_id))
        if not technology:
            raise HTTPException(status_code=404, detail="Technology not found")
        
        # Создаем связь
        link = await supabase_service.create_direction_technology(
            direction_id=str(direction_id),
            technology_id=str(technology_id),
            order_index=order_index
        )
        
        return {
            "link": link,
            "message": f"Technology '{technology['name']}' linked to direction '{direction['name']}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking technology to direction: {str(e)}")


@router.post(
    "/technologies/{technology_id}/competencies/{competency_id}",
    summary="Связать компетенцию с технологией",
    description="Добавляет компетенцию к технологии"
)
async def link_competency_to_technology(
    technology_id: UUID,
    competency_id: UUID,
    order_index: Optional[int] = None,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Связать компетенцию с технологией"""
    try:
        # Проверяем существование технологии
        technology = await supabase_service.get_technology(str(technology_id))
        if not technology:
            raise HTTPException(status_code=404, detail="Technology not found")
        
        # Проверяем существование компетенции (простая проверка)
        # Можно добавить метод get_competency если нужно
        
        # Создаем связь
        link = await supabase_service.create_technology_competency(
            technology_id=str(technology_id),
            competency_id=str(competency_id),
            order_index=order_index
        )
        
        return {
            "link": link,
            "message": f"Competency linked to technology '{technology['name']}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking competency to technology: {str(e)}")


@router.post(
    "/directions/{direction_id}/competencies/{competency_id}",
    summary="Связать компетенцию с направлением",
    description="Добавляет общую компетенцию к направлению"
)
async def link_competency_to_direction(
    direction_id: UUID,
    competency_id: UUID,
    order_index: Optional[int] = None,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Связать компетенцию с направлением"""
    try:
        # Проверяем существование направления
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        # Создаем связь
        link = await supabase_service.create_direction_competency(
            direction_id=str(direction_id),
            competency_id=str(competency_id),
            order_index=order_index
        )
        
        return {
            "link": link,
            "message": f"Competency linked to direction '{direction['name']}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking competency to direction: {str(e)}")


# === BATCH OPERATIONS ===

class BatchTechnologyLink(BaseModel):
    technology_ids: List[UUID]


@router.post(
    "/directions/{direction_id}/technologies/batch",
    summary="Массовое добавление технологий к направлению",
    description="Добавляет несколько технологий к направлению за раз"
)
async def batch_link_technologies_to_direction(
    direction_id: UUID,
    batch_data: BatchTechnologyLink,
    supabase_service: SupabaseService = Depends(get_supabase_service),
    user_id: str = Depends(get_current_user_id)
):
    """Массовое добавление технологий к направлению"""
    try:
        direction = await supabase_service.get_direction(str(direction_id))
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        
        links = []
        for idx, tech_id in enumerate(batch_data.technology_ids, start=1):
            try:
                link = await supabase_service.create_direction_technology(
                    direction_id=str(direction_id),
                    technology_id=str(tech_id),
                    order_index=idx
                )
                links.append(link)
            except Exception as e:
                # Пропускаем если связь уже существует
                continue
        
        return {
            "links": links,
            "message": f"Linked {len(links)} technologies to direction '{direction['name']}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error batch linking technologies: {str(e)}")
