from typing import Annotated

from fastapi import Depends

from domain.services.school_services import SchoolService
from domain.services.student_services import StudentService
from infrastructure.database.db_engine import AsyncSessionLocal
from infrastructure.repositories.postgres import PostgresRepository


def get_repository() -> PostgresRepository:
    return PostgresRepository(session_factory=AsyncSessionLocal)


def get_school_service(
    repo: Annotated[PostgresRepository, Depends(get_repository)],
) -> SchoolService:
    return SchoolService(repository=repo)


def get_student_service(
    repo: Annotated[PostgresRepository, Depends(get_repository)],
) -> StudentService:
    return StudentService(repository=repo)
