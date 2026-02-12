from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.models.invoice import InvoiceStatus
from infrastructure.database.db_engine import Base



class StudentTable(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class SchoolTable(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class SchoolStudentsTable(Base):
    __tablename__ = "school_students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String, nullable=False)

    school: Mapped["SchoolTable"] = relationship("SchoolTable")
    student: Mapped["StudentTable"] = relationship("StudentTable")


class InvoiceTable(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(SAEnum(InvoiceStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)

    student: Mapped["StudentTable"] = relationship("StudentTable")
    school: Mapped["SchoolTable"] = relationship("SchoolTable")


class PaymentTable(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    invoice: Mapped["InvoiceTable"] = relationship("InvoiceTable")
