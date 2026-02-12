from typing import Annotated
from fastapi_pagination import Page, Params

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_student_service, get_student_repository
from domain.models.student import Student, StudentCreate
from domain.services.student_services import StudentService
from infrastructure.repositories.postgres import StudentRepository


router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=Page[Student])
async def list_students(
    repo: Annotated[StudentRepository, Depends(get_student_repository)],
    params: Params = Depends(),
) -> Page[Student]:
    offset = (params.page - 1) * params.size
    students, total = await repo.get_students(offset=offset, limit=params.size)
    return Page.create(items=students, params=params, total=total)


@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    repo: Annotated[StudentRepository, Depends(get_student_repository)],
) -> Student:
    return await repo.create_student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        email=student_data.email,
        age=student_data.age,
    )


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    repo: Annotated[StudentRepository, Depends(get_student_repository)],
) -> Student:
    students, _ = await repo.get_students(filters={"id": student_id}, limit=1)
    if not students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[0]


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    repo: Annotated[StudentRepository, Depends(get_student_repository)],
):
    deleted = await repo.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")


@router.get("/{student_id}/financial-status", response_model=Student)
async def get_student_financial_status(
    student_id: int,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> Student:
    student = await service.financial_status(student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
