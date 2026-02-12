from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from domain.models.student import Student


class School(BaseModel):
    id: int
    ref: str
    name: str
    created_at: datetime
    students: list[Student] = []
    total_debt: Optional[Decimal] = None


class SchoolCreate(BaseModel):
    ref: str
    name: str
