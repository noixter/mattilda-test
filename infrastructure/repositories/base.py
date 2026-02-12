from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional
from domain.models.student import Student
from domain.models.school import School
from domain.models.invoice import Invoice, Payment


class BaseRepository(ABC):
    @abstractmethod
    async def get_students(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        school_id: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Student], int]: ...

    @abstractmethod
    async def get_schools(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[School], int]: ...

    @abstractmethod
    async def get_invoices(
        self,
        *,
        school_id: Optional[int] = None,
        student_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Invoice], int]: ...

    @abstractmethod
    async def get_payments(
        self,
        *,
        student_id: Optional[int] = None,
    ) -> list[Payment]: ...
