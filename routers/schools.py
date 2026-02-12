import logging
from typing import Annotated
from fastapi_pagination import Page, Params

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_school_service, get_school_repository
from domain.models.school import School, SchoolCreate
from domain.models.student import Student
from domain.services.school_services import SchoolService
from infrastructure.repositories.postgres import SchoolRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("/", response_model=Page[School])
async def list_schools(
    repo: Annotated[SchoolRepository, Depends(get_school_repository)],
    params: Params = Depends(),
) -> Page[School]:
    offset = (params.page - 1) * params.size
    schools, total = await repo.get_schools(offset=offset, limit=params.size)
    return Page.create(items=schools, params=params, total=total)


@router.post("/", response_model=School, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    repo: Annotated[SchoolRepository, Depends(get_school_repository)],
) -> School:
    return await repo.create_school(
        ref=school_data.ref,
        name=school_data.name,
    )


@router.get("/{school_id}", response_model=School)
async def get_school(
    school_id: int,
    repo: Annotated[SchoolRepository, Depends(get_school_repository)],
) -> School:
    schools, _ = await repo.get_schools(filters={"id": school_id}, limit=1)
    if not schools:
        raise HTTPException(status_code=404, detail="School not found")
    return schools[0]


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    repo: Annotated[SchoolRepository, Depends(get_school_repository)],
):
    deleted = await repo.delete_school(school_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="School not found")


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
