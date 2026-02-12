from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import field_validator


class StudentStatus(str, Enum):
    # Status to be handle in history table SchoolStudentsTable
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    age: int

    
class Student(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    created_at: datetime
    total_paid: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not (0 < v < 18):
            raise ValueError("Age must be between 0 and 18")
        return v
