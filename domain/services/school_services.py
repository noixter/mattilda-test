from typing import Any, Mapping
from decimal import Decimal

from domain.models.school import School
from domain.models.student import StudentStatus
from domain.models.invoice import InvoiceStatus
from infrastructure.repositories.base import BaseRepository


class SchoolService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def get_school_students(
        self,
        *,
        filters: Mapping[str, Any],
        active: bool = True,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[School, int] | None:
        schools, _ = await self.repository.get_schools(filters=filters)
        if not schools:
            return None
        
        # TODO: should we replace this with a specific get_school_by_id method?
        school = schools[0]
        
        status_filter = StudentStatus.ACTIVE.value if active else StudentStatus.DEACTIVATED.value
        
        students, total_students = await self.repository.get_students(
            school_id=school.id,
            status=status_filter,
            offset=offset,
            limit=limit,
        )
        
        school.students = students
        return school, total_students

    # TODO: this might be better as an SQL query
    async def get_school_debt(self, *, school_id: int) -> School:
        schools, _ = await self.repository.get_schools(filters={"id": school_id})
        if not schools:
            return None
        school = schools[0]

        invoices, _ = await self.repository.get_invoices(school_id=school.id)
        
        pending_invoices = list(filter(lambda invoice: invoice.status == InvoiceStatus.PENDING, invoices))
        total_debt = sum(inv.value for inv in pending_invoices)
        
        school.total_debt = Decimal(total_debt)
        return school
