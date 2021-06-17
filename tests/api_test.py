import pytest
from httpx import AsyncClient

from .api_fixture import app

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("path", ["people", "people/1", "scheduled_jobs", "scheduled_jobs/1"])
async def test_people_api_get_paths(path):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/v1.0/{path}", headers={"auth": "user"})

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["person"])
async def test_missing_people_api_get_paths(path):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/v1.0/{path}", headers={"auth": "user"})

    assert response.status_code == 404


@pytest.mark.parametrize("path", ["people"])
async def test_people_api_post_paths(path):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/v1.0/{path}", headers={"auth": "user"})

    assert response.status_code == 200
