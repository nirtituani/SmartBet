from app.services.football_api import get_upcoming_matches, get_match_detail
from app.models.match import Match, MatchDetail


def test_get_upcoming_matches_returns_8():
    matches = get_upcoming_matches()
    assert len(matches) == 8


def test_all_matches_are_match_instances():
    for m in get_upcoming_matches():
        assert isinstance(m, Match)


def test_match_ids_are_sequential():
    ids = [m.id for m in get_upcoming_matches()]
    assert ids == list(range(1, 9))


def test_odds_are_realistic():
    for m in get_upcoming_matches():
        assert 1.1 < m.home_odds < 10.0
        assert 2.5 < m.draw_odds < 5.0
        assert 1.1 < m.away_odds < 10.0


def test_get_match_detail_returns_detail_for_valid_id():
    detail = get_match_detail(1)
    assert isinstance(detail, MatchDetail)
    assert detail.match.id == 1
    assert len(detail.home_form) == 5
    assert len(detail.away_form) == 5
    assert len(detail.h2h) == 5
    assert len(detail.odds_comparison) == 4


def test_get_match_detail_returns_none_for_invalid_id():
    assert get_match_detail(999) is None


def test_mock_data_is_deterministic():
    m1 = get_upcoming_matches()
    m2 = get_upcoming_matches()
    assert m1[0].home_odds == m2[0].home_odds
