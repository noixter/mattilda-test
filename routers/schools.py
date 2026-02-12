import logging
from typing import Annotated
from fastapi_pagination import Page, Params

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_school_service
from domain.models.school import School
from domain.models.student import Student
from domain.services.school_services import SchoolService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("/", response_model=Page[School])
async def list_schools(
    service: Annotated[SchoolService, Depends(get_school_service)],
    params: Params = Depends(),
) -> Page[School]:
    offset = (params.page - 1) * params.size
    schools, total = await service.repository.get_schools(offset=offset, limit=params.size)
    return Page.create(items=schools, params=params, total=total)


@router.get("/{school_id}/students", response_model=Page[Student])
async def list_school_students(
    school_id: int,
    service: Annotated[SchoolService, Depends(get_school_service)],
    active: bool = True,
    params: Params = Depends(),
) -> Page[Student]:
    offset = (params.page - 1) * params.size
    result = await service.get_school_students(
        filters={"id": school_id}, 
        active=active,
        offset=offset,
        limit=params.size,
    )
    if not result:
        raise HTTPException(status_code=404, detail="School not found")
    
    school, total = result
    return Page.create(items=school.students, params=params, total=total)


@router.get("/{school_id}/debt", response_model=School)
async def get_school_debt(
    school_id: int,
    service: Annotated[SchoolService, Depends(get_school_service)],
) -> School:
    try:
        school_debt = await service.get_school_debt(school_id=school_id)
        if not school_debt:
            raise HTTPException(status_code=404, detail="School not found")
        return school_debt
    except Exception as e:
        logger.exception("Error getting school debt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
