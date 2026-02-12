from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, field_serializer
from .school import School
from .student import Student


class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class Invoice(BaseModel):
    id: int
    ref: str
    student: Student
    school: School
    value: Decimal
    date: datetime
    status: InvoiceStatus
    created_at: datetime

    # TODO: define a better serialization strategy here
    @field_serializer("school")
    def serialize_school(self, school: School):
        return school.id

    @field_serializer("student")
    def serialize_student(self, student: Student):
        return student.id


class Payment(BaseModel):
    id: int
    ref: str
    invoice: Invoice
    value: Decimal
    date: datetime
    created_at: datetime
