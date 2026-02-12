from typing import Annotated
from fastapi_pagination import Page, Params

from fastapi import APIRouter, Depends

from dependencies import get_school_service
from domain.models.invoice import Invoice
from domain.services.school_services import SchoolService

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=Page[Invoice])
async def list_invoices(
    service: Annotated[SchoolService, Depends(get_school_service)],
    school_id: int | None = None,
    student_id: int | None = None,
    params: Params = Depends(),
) -> Page[Invoice]:
    offset = (params.page - 1) * params.size
    invoices, total = await service.repository.get_invoices(
        school_id=school_id,
        student_id=student_id,
        offset=offset,
        limit=params.size,
    )
    return Page.create(items=invoices, params=params, total=total)
