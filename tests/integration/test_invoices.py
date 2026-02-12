import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestIntegrationInvoices:
    async def test_list_invoices_empty(self, client: AsyncClient):
        response = await client.get("/invoices/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1

    async def test_list_invoices_with_data(self, client: AsyncClient, sample_invoices):
        response = await client.get("/invoices/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

        invoice_refs = [invoice["ref"] for invoice in data["items"]]
        assert "INV001" in invoice_refs
        assert "INV002" in invoice_refs
        assert "INV003" in invoice_refs

    async def test_list_invoices_pagination(self, client: AsyncClient, sample_invoices):
        response = await client.get("/invoices/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2

        response = await client.get("/invoices/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 1
        assert data["page"] == 2

    async def test_list_invoices_filter_by_student(
        self, client: AsyncClient, sample_invoices, sample_students
    ):
        student_id = sample_students[0].id
        response = await client.get(f"/invoices/?student_id={student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["ref"] == "INV001"

    async def test_list_invoices_filter_by_school(
        self, client: AsyncClient, sample_invoices, sample_schools
    ):
        school_id = sample_schools[0].id
        response = await client.get(f"/invoices/?school_id={school_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

        invoice_refs = [invoice["ref"] for invoice in data["items"]]
        assert "INV001" in invoice_refs
        assert "INV002" in invoice_refs
