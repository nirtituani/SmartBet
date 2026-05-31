import pytest
from app.services.football_api import get_upcoming_matches, get_match_detail
from app.models.match import Match, MatchDetail


@pytest.fixture(autouse=True)
def use_mock_data(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "football_api_key", "")
    monkeypatch.setattr(config.settings, "wc26_api_key", "")


@pytest.mark.asyncio
async def test_get_upcoming_matches_returns_72():
    matches = await get_upcoming_matches()
    assert len(matches) == 72


@pytest.mark.asyncio
async def test_all_matches_are_match_instances():
    for m in await get_upcoming_matches():
        assert isinstance(m, Match)


@pytest.mark.asyncio
async def test_match_ids_are_sequential():
    ids = [m.id for m in await get_upcoming_matches()]
    assert ids == list(range(1, 73))


@pytest.mark.asyncio
async def test_odds_are_realistic():
    for m in await get_upcoming_matches():
        assert 1.1 < m.home_odds < 10.0
        assert 2.5 < m.draw_odds < 5.0
        assert 1.1 < m.away_odds < 10.0


@pytest.mark.asyncio
async def test_get_match_detail_returns_detail_for_valid_id():
    detail = await get_match_detail(1)
    assert isinstance(detail, MatchDetail)
    assert detail.match.id == 1
    assert len(detail.home_form) == 5
    assert len(detail.away_form) == 5
    assert len(detail.h2h) == 5
    assert len(detail.odds_comparison) == 4


@pytest.mark.asyncio
async def test_get_match_detail_returns_none_for_invalid_id():
    assert await get_match_detail(999) is None


@pytest.mark.asyncio
async def test_mock_data_is_deterministic():
    m1 = await get_upcoming_matches()
    m2 = await get_upcoming_matches()
    assert m1[0].home_odds == m2[0].home_odds
