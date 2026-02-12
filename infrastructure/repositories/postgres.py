import logging
from typing import Any, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from domain.models.student import Student
from domain.models.school import School
from domain.models.invoice import Invoice, Payment
from infrastructure.repositories.base import BaseRepository
from infrastructure.database.orm import (
    StudentTable,
    SchoolTable,
    InvoiceTable,
    PaymentTable,
    SchoolStudentsTable,
)


logger = logging.getLogger(__name__)


class PostgresRepository(BaseRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    def _filter_by_attributes(self, stmt, filters, table):
        if not filters:
            return stmt

        for key, value in filters.items():
            if not hasattr(table, key):
                logger.debug(f"Attribute {key} not found in table {table}")
                continue
            stmt = stmt.where(getattr(table, key) == value)
        return stmt

    async def get_students(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        school_id: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Student], int]:
        async with self.session_factory() as session:
            stmt = select(StudentTable)
            
            if school_id or status:
                stmt = stmt.join(SchoolStudentsTable, StudentTable.id == SchoolStudentsTable.student_id)
                
                if school_id:
                    stmt = stmt.where(SchoolStudentsTable.school_id == school_id)
                if status:
                    stmt = stmt.where(SchoolStudentsTable.status == status)

            stmt = self._filter_by_attributes(stmt, filters, StudentTable)
            stmt = stmt.order_by(StudentTable.id)

            # Get total count before pagination
            count_result = await session.execute(stmt)
            total = len(count_result.scalars().all())
            
            paginated_stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(paginated_stmt)
            students = result.scalars().all()
            
            return [
                Student(
                    id=student.id,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.email,
                    age=student.age,
                    created_at=student.created_at
                )
                for student in students
            ], total

    async def get_schools(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[School], int]:
        async with self.session_factory() as session:
            stmt = select(SchoolTable)
            stmt = self._filter_by_attributes(stmt, filters, SchoolTable)
            stmt = stmt.order_by(SchoolTable.id)
            
            # Get total count before pagination
            count_result = await session.execute(stmt)
            total = len(count_result.scalars().all())
            
            paginated_stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(paginated_stmt)
            schools = result.scalars().all()
            
            return [
                School(
                    id=school.id,
                    ref=school.ref,
                    name=school.name,
                    created_at=school.created_at,
                )
                for school in schools
            ], total

    async def get_invoices(
        self,
        *,
        school_id: Optional[int] = None,
        student_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Invoice], int]:
        async with self.session_factory() as session:
            stmt = select(InvoiceTable).options(
                selectinload(InvoiceTable.student),
                selectinload(InvoiceTable.school)
            )
            
            if school_id:
                stmt = stmt.where(InvoiceTable.school_id == school_id)
            if student_id:
                stmt = stmt.where(InvoiceTable.student_id == student_id)

            stmt = stmt.order_by(InvoiceTable.created_at)
            
            # Get total count before pagination
            count_result = await session.execute(stmt)
            total = len(count_result.scalars().all())
            
            paginated_stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(paginated_stmt)
            invoices = result.scalars().all()
            
            return [
                Invoice(
                    id=invoice.id,
                    ref=invoice.ref,
                    value=invoice.value,
                    date=invoice.date,
                    status=invoice.status,
                    created_at=invoice.created_at,
                    student=Student(
                        id=invoice.student.id,
                        first_name=invoice.student.first_name,
                        last_name=invoice.student.last_name,
                        email=invoice.student.email,
                        age=invoice.student.age,
                        created_at=invoice.student.created_at
                    ),
                    school=School(
                        id=invoice.school.id,
                        ref=invoice.school.ref,
                        name=invoice.school.name,
                        created_at=invoice.school.created_at
                    ),
                )
                for invoice in invoices
            ], total

    async def get_payments(
        self,
        *,
        student_id: Optional[int] = None,
    ) -> list[Payment]:
        async with self.session_factory() as session:
            stmt = select(PaymentTable).options(
                selectinload(PaymentTable.invoice).selectinload(InvoiceTable.student),
                selectinload(PaymentTable.invoice).selectinload(InvoiceTable.school)
            )
            
            if student_id:
                stmt = stmt.join(InvoiceTable).where(InvoiceTable.student_id == student_id)
                
            result = await session.execute(stmt)
            payments = result.scalars().all()
            
            return [
                Payment(
                    id=payment.id,
                    ref=payment.ref,
                    value=payment.value,
                    date=payment.date,
                    created_at=payment.created_at,
                    invoice=Invoice(
                        id=payment.invoice.id,
                        ref=payment.invoice.ref,
                        value=payment.invoice.value,
                        date=payment.invoice.date,
                        status=payment.invoice.status,
                        created_at=payment.invoice.created_at,
                        student=Student(
                            id=payment.invoice.student.id,
                            first_name=payment.invoice.student.first_name,
                            last_name=payment.invoice.student.last_name,
                            email=payment.invoice.student.email,
                            age=payment.invoice.student.age,
                            created_at=payment.invoice.student.created_at
                        ),
                        school=School(
                            id=payment.invoice.school.id,
                            ref=payment.invoice.school.ref,
                            name=payment.invoice.school.name,
                            created_at=payment.invoice.school.created_at
                        ),
                    )
                )
                for payment in payments
            ]
