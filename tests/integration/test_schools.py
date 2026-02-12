import pytest
from httpx import AsyncClient


class TestIntegrationSchools:
    @pytest.mark.asyncio
    async def test_list_schools_empty(self, client: AsyncClient):
        response = await client.get("/schools/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_schools_with_data(self, client: AsyncClient, sample_schools):
        response = await client.get("/schools/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

        school_names = [school["name"] for school in data["items"]]
        assert "Lincoln High School" in school_names
        assert "Washington Academy" in school_names
        assert "Jefferson Elementary" in school_names

    @pytest.mark.asyncio
    async def test_list_schools_pagination(self, client: AsyncClient, sample_schools):
        response = await client.get("/schools/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2

        response = await client.get("/schools/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 1
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_get_school_debt(
        self, client: AsyncClient, sample_schools, sample_invoices
    ):
        school_id = sample_schools[0].id
        response = await client.get(f"/schools/{school_id}/debt")
        assert response.status_code == 200
        data = response.json()
        assert "total_debt" in data
        assert data["id"] == school_id

    @pytest.mark.asyncio
    async def test_get_school_debt_not_found(self, client: AsyncClient):
        response = await client.get("/schools/99999/debt")
        assert response.status_code == 404
