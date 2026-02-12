import pytest
from httpx import AsyncClient


class TestIntegrationStudents:
    @pytest.mark.asyncio
    async def test_list_students_empty(self, client: AsyncClient):
        response = await client.get("/students/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_students_with_data(self, client: AsyncClient, sample_students):
        response = await client.get("/students/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

        student_emails = [student["email"] for student in data["items"]]
        assert "alice@test.com" in student_emails
        assert "bob@test.com" in student_emails
        assert "charlie@test.com" in student_emails

    @pytest.mark.asyncio
    async def test_list_students_pagination(self, client: AsyncClient, sample_students):
        response = await client.get("/students/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2

        response = await client.get("/students/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 1
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_financial_status_with_invoices_and_payments(
        self, client: AsyncClient, sample_students, sample_invoices
    ):
        student_id = sample_students[0].id
        response = await client.get(f"/students/{student_id}/financial-status")
        assert response.status_code == 200
        data = response.json()
        assert "total_paid" in data
        assert "total_debt" in data

    @pytest.mark.asyncio
    async def test_financial_status_student_not_found(self, client: AsyncClient):
        response = await client.get("/students/99999/financial-status")
        assert response.status_code == 404
