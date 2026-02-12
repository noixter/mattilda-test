import logging
from typing import Any, Mapping, Optional
from datetime import datetime

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from domain.models.student import Student
from domain.models.school import School
from domain.models.invoice import Invoice, Payment
from infrastructure.database.orm import (
    StudentTable,
    SchoolTable,
    InvoiceTable,
    PaymentTable,
    SchoolStudentsTable,
)


logger = logging.getLogger(__name__)


def _filter_by_attributes(stmt, filters, table):
    """Helper function to apply filters to a SQLAlchemy statement."""
    if not filters:
        return stmt

    for key, value in filters.items():
        if not hasattr(table, key):
            logger.debug(f"Attribute {key} not found in table {table}")
            continue
        stmt = stmt.where(getattr(table, key) == value)
    return stmt


class StudentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

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
                stmt = stmt.join(
                    SchoolStudentsTable,
                    StudentTable.id == SchoolStudentsTable.student_id,
                )

                if school_id:
                    stmt = stmt.where(SchoolStudentsTable.school_id == school_id)
                if status:
                    stmt = stmt.where(SchoolStudentsTable.status == status)

            stmt = _filter_by_attributes(stmt, filters, StudentTable)
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
                    created_at=student.created_at,
                )
                for student in students
            ], total

    async def create_student(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        age: int,
    ) -> Student:
        async with self.session_factory() as session:
            student_table = StudentTable(
                first_name=first_name,
                last_name=last_name,
                email=email,
                age=age,
                created_at=datetime.now(),
            )
            session.add(student_table)
            await session.commit()
            await session.refresh(student_table)

            return Student(
                id=student_table.id,
                first_name=student_table.first_name,
                last_name=student_table.last_name,
                email=student_table.email,
                age=student_table.age,
                created_at=student_table.created_at,
            )

    async def delete_student(self, student_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = sql_delete(StudentTable).where(StudentTable.id == student_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


class SchoolRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get_schools(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[School], int]:
        async with self.session_factory() as session:
            stmt = select(SchoolTable)
            stmt = _filter_by_attributes(stmt, filters, SchoolTable)
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

    async def create_school(
        self,
        *,
        ref: str,
        name: str,
    ) -> School:
        async with self.session_factory() as session:
            school_table = SchoolTable(ref=ref, name=name, created_at=datetime.now())
            session.add(school_table)
            await session.commit()
            await session.refresh(school_table)

            return School(
                id=school_table.id,
                ref=school_table.ref,
                name=school_table.name,
                created_at=school_table.created_at,
            )

    async def delete_school(self, school_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = sql_delete(SchoolTable).where(SchoolTable.id == school_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


class InvoiceRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

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
                selectinload(InvoiceTable.student), selectinload(InvoiceTable.school)
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
                        created_at=invoice.student.created_at,
                    ),
                    school=School(
                        id=invoice.school.id,
                        ref=invoice.school.ref,
                        name=invoice.school.name,
                        created_at=invoice.school.created_at,
                    ),
                )
                for invoice in invoices
            ], total

    async def create_invoice(
        self,
        *,
        ref: str,
        student_id: int,
        school_id: int,
        value: float,
        date: datetime,
        status: str,
    ) -> Invoice:
        async with self.session_factory() as session:
            invoice_table = InvoiceTable(
                ref=ref,
                student_id=student_id,
                school_id=school_id,
                value=value,
                date=date,
                status=status,
                created_at=datetime.now(),
            )
            session.add(invoice_table)
            await session.commit()
            await session.refresh(invoice_table)

            stmt = (
                select(InvoiceTable)
                .options(
                    selectinload(InvoiceTable.student),
                    selectinload(InvoiceTable.school),
                )
                .where(InvoiceTable.id == invoice_table.id)
            )
            result = await session.execute(stmt)
            invoice = result.scalar_one()

            return Invoice(
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
                    created_at=invoice.student.created_at,
                ),
                school=School(
                    id=invoice.school.id,
                    ref=invoice.school.ref,
                    name=invoice.school.name,
                    created_at=invoice.school.created_at,
                ),
            )

    async def delete_invoice(self, invoice_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = sql_delete(InvoiceTable).where(InvoiceTable.id == invoice_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def get_payments(
        self,
        *,
        student_id: Optional[int] = None,
    ) -> list[Payment]:
        async with self.session_factory() as session:
            stmt = select(PaymentTable).options(
                selectinload(PaymentTable.invoice).selectinload(InvoiceTable.student),
                selectinload(PaymentTable.invoice).selectinload(InvoiceTable.school),
            )

            if student_id:
                stmt = stmt.join(InvoiceTable).where(
                    InvoiceTable.student_id == student_id
                )

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
                            created_at=payment.invoice.student.created_at,
                        ),
                        school=School(
                            id=payment.invoice.school.id,
                            ref=payment.invoice.school.ref,
                            name=payment.invoice.school.name,
                            created_at=payment.invoice.school.created_at,
                        ),
                    ),
                )
                for payment in payments
            ]

    async def create_payment(
        self,
        *,
        ref: str,
        invoice_id: int,
        value: float,
        date: datetime,
    ) -> Payment:
        async with self.session_factory() as session:
            payment_table = PaymentTable(
                ref=ref,
                invoice_id=invoice_id,
                value=value,
                date=date,
                created_at=datetime.now(),
            )
            session.add(payment_table)
            await session.commit()
            await session.refresh(payment_table)

            # Reload with relationships
            stmt = (
                select(PaymentTable)
                .options(
                    selectinload(PaymentTable.invoice).selectinload(
                        InvoiceTable.student
                    ),
                    selectinload(PaymentTable.invoice).selectinload(
                        InvoiceTable.school
                    ),
                )
                .where(PaymentTable.id == payment_table.id)
            )
            result = await session.execute(stmt)
            payment = result.scalar_one()

            return Payment(
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
                        created_at=payment.invoice.student.created_at,
                    ),
                    school=School(
                        id=payment.invoice.school.id,
                        ref=payment.invoice.school.ref,
                        name=payment.invoice.school.name,
                        created_at=payment.invoice.school.created_at,
                    ),
                ),
            )

    async def delete_payment(self, payment_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = sql_delete(PaymentTable).where(PaymentTable.id == payment_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


# TODO: This class is not longer needed, it was created to avoid injecting multiple dependencies to services
class PostgresRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.student_repo = StudentRepository(session_factory)
        self.school_repo = SchoolRepository(session_factory)
        self.invoice_repo = InvoiceRepository(session_factory)

    async def get_students(self, **kwargs):
        return await self.student_repo.get_students(**kwargs)

    async def get_schools(self, **kwargs):
        return await self.school_repo.get_schools(**kwargs)

    async def get_invoices(self, **kwargs):
        return await self.invoice_repo.get_invoices(**kwargs)

    async def get_payments(self, **kwargs):
        return await self.invoice_repo.get_payments(**kwargs)
