from decimal import Decimal
from typing import Optional

from domain.models.student import Student
from domain.models.invoice import InvoiceStatus
from infrastructure.repositories.base import BaseRepository


class StudentService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    # TODO this won't scale as computation is performed in memory not in DB
    async def financial_status(self, student_id: int) -> Optional[Student]:
        students, _ = await self.repository.get_students(
            filters={"id": student_id}, limit=1
        )
        if not students:
            return None
        student = students[0]

        # TODO: maybe a greater limit should be used here, so far the default limit is 100
        invoices, _ = await self.repository.get_invoices(student_id=student.id)
        payments = await self.repository.get_payments(student_id=student.id)

        total_paid = sum(payment.value for payment in payments)
        pending_invoices = [
            inv for inv in invoices if inv.status == InvoiceStatus.PENDING
        ]
        total_debt = sum(inv.value for inv in pending_invoices)

        student.total_paid = Decimal(total_paid)
        student.total_debt = Decimal(total_debt)

        return student
