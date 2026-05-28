import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_upcoming_matches_returns_8(client):
    r = await client.get("/api/v1/matches/upcoming")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 8
    assert data[0]["home_team"]["name"] == "Brazil"


@pytest.mark.asyncio
async def test_match_predictions_valid_id(client):
    r = await client.get("/api/v1/matches/1/predictions")
    assert r.status_code == 200
    data = r.json()
    assert "prediction" in data
    assert data["prediction"]["confidence_percentage"] >= 0


@pytest.mark.asyncio
async def test_match_predictions_invalid_id(client):
    r = await client.get("/api/v1/matches/999/predictions")
    assert r.status_code == 404
