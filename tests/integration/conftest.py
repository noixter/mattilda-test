import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from infrastructure.database.db_engine import Base
from infrastructure.database.orm import StudentTable, SchoolTable, InvoiceTable


# in memory database for integration tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from infrastructure.database.db_engine import AsyncSessionLocal
    from dependencies import (
        get_student_repository,
        get_school_repository,
        get_invoice_repository,
    )
    from infrastructure.repositories.postgres import (
        StudentRepository,
        SchoolRepository,
        InvoiceRepository,
    )

    def override_student_repo():
        return StudentRepository(session_factory=TestAsyncSessionLocal)

    def override_school_repo():
        return SchoolRepository(session_factory=TestAsyncSessionLocal)

    def override_invoice_repo():
        return InvoiceRepository(session_factory=TestAsyncSessionLocal)

    app.dependency_overrides[get_student_repository] = override_student_repo
    app.dependency_overrides[get_school_repository] = override_school_repo
    app.dependency_overrides[get_invoice_repository] = override_invoice_repo

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def sample_students(db_session: AsyncSession):
    students = [
        StudentTable(
            first_name="Alice",
            last_name="Johnson",
            email="alice@test.com",
            age=16,
        ),
        StudentTable(
            first_name="Bob",
            last_name="Smith",
            email="bob@test.com",
            age=15,
        ),
        StudentTable(
            first_name="Charlie",
            last_name="Brown",
            email="charlie@test.com",
            age=17,
        ),
    ]
    db_session.add_all(students)
    await db_session.commit()
    return students


@pytest.fixture(scope="function")
async def sample_schools(db_session: AsyncSession):
    schools = [
        SchoolTable(
            ref="SCH001",
            name="Lincoln High School",
        ),
        SchoolTable(
            ref="SCH002",
            name="Washington Academy",
        ),
        SchoolTable(
            ref="SCH003",
            name="Jefferson Elementary",
        ),
    ]
    db_session.add_all(schools)
    await db_session.commit()
    return schools


@pytest.fixture(scope="function")
async def sample_invoices(db_session: AsyncSession, sample_students, sample_schools):
    from decimal import Decimal
    from datetime import datetime
    from domain.models.invoice import InvoiceStatus

    invoices = [
        InvoiceTable(
            ref="INV001",
            student_id=sample_students[0].id,
            school_id=sample_schools[0].id,
            value=Decimal("500.00"),
            date=datetime.now(),
            status=InvoiceStatus.PENDING,
        ),
        InvoiceTable(
            ref="INV002",
            student_id=sample_students[1].id,
            school_id=sample_schools[0].id,
            value=Decimal("600.00"),
            date=datetime.now(),
            status=InvoiceStatus.PAID,
        ),
        InvoiceTable(
            ref="INV003",
            student_id=sample_students[2].id,
            school_id=sample_schools[1].id,
            value=Decimal("450.00"),
            date=datetime.now(),
            status=InvoiceStatus.PENDING,
        ),
    ]
    db_session.add_all(invoices)
    await db_session.commit()
    return invoices
