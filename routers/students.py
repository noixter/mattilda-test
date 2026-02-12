from typing import Annotated
from fastapi_pagination import Page, Params

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_school_service, get_student_service
from domain.models.student import Student
from domain.services.school_services import SchoolService
from domain.services.student_services import StudentService


router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=Page[Student])
async def list_students(
    service: Annotated[SchoolService, Depends(get_school_service)],
    params: Params = Depends(),
) -> Page[Student]:
    offset = (params.page - 1) * params.size
    students, total = await service.repository.get_students(offset=offset, limit=params.size)
    return Page.create(items=students, params=params, total=total)


@router.get("/{student_id}/financial-status", response_model=Student)
async def get_student_financial_status(
    student_id: int,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> Student:
    student = await service.financial_status(student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
