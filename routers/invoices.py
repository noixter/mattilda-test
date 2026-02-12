from typing import Annotated
from datetime import datetime
from decimal import Decimal
from fastapi_pagination import Page, Params
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_invoice_repository
from domain.models.invoice import Invoice, Payment
from infrastructure.repositories.postgres import InvoiceRepository

router = APIRouter(prefix="/invoices", tags=["invoices"])


class InvoiceCreate(BaseModel):
    ref: str
    student_id: int
    school_id: int
    value: Decimal
    date: datetime
    status: str


class PaymentCreate(BaseModel):
    ref: str
    invoice_id: int
    value: Decimal
    date: datetime


@router.get("/", response_model=Page[Invoice])
async def list_invoices(
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
    school_id: int | None = None,
    student_id: int | None = None,
    params: Params = Depends(),
) -> Page[Invoice]:
    offset = (params.page - 1) * params.size
    invoices, total = await repo.get_invoices(
        school_id=school_id,
        student_id=student_id,
        offset=offset,
        limit=params.size,
    )
    return Page.create(items=invoices, params=params, total=total)


@router.post("/", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
) -> Invoice:
    return await repo.create_invoice(
        ref=invoice_data.ref,
        student_id=invoice_data.student_id,
        school_id=invoice_data.school_id,
        value=Decimal(invoice_data.value),
        date=invoice_data.date,
        status=invoice_data.status,
    )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
):
    deleted = await repo.delete_invoice(invoice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.get("/payments", response_model=list[Payment])
async def list_payments(
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
    student_id: int | None = None,
) -> list[Payment]:
    return await repo.get_payments(student_id=student_id)


@router.post("/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
) -> Payment:
    return await repo.create_payment(
        ref=payment_data.ref,
        invoice_id=payment_data.invoice_id,
        value=float(payment_data.value),
        date=payment_data.date,
    )


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
):
    deleted = await repo.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
