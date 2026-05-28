import asyncio
import random
from datetime import date, timedelta
from typing import Any

import httpx

from app.core.config import settings
from app.models.match import (
    BookmakerOdds, FormResult, H2HResult, Match, MatchDetail, Team,
)

# ── Static meta (flag emoji + approximate FIFA rank) ──────────────────────────

_TEAM_META: dict[str, tuple[str, int]] = {
    "Brazil": ("🇧🇷", 1), "France": ("🇫🇷", 2), "Argentina": ("🇦🇷", 3),
    "Spain": ("🇪🇸", 4), "England": ("🏴󠁧󠁢󠁥󠁮󠁧󠁿", 5), "Germany": ("🇩🇪", 6),
    "Portugal": ("🇵🇹", 7), "Netherlands": ("🇳🇱", 8), "Italy": ("🇮🇹", 9),
    "Croatia": ("🇭🇷", 10), "Uruguay": ("🇺🇾", 11), "Colombia": ("🇨🇴", 12),
    "Mexico": ("🇲🇽", 13), "USA": ("🇺🇸", 14), "Morocco": ("🇲🇦", 15),
    "Japan": ("🇯🇵", 16), "Senegal": ("🇸🇳", 17), "Switzerland": ("🇨🇭", 18),
    "Denmark": ("🇩🇰", 19), "Austria": ("🇦🇹", 20), "Belgium": ("🇧🇪", 21),
    "Poland": ("🇵🇱", 22), "Serbia": ("🇷🇸", 23), "South Korea": ("🇰🇷", 24),
    "Canada": ("🇨🇦", 25), "Australia": ("🇦🇺", 26), "Ecuador": ("🇪🇨", 27),
    "Hungary": ("🇭🇺", 28), "Turkey": ("🇹🇷", 29), "Chile": ("🇨🇱", 30),
    "Paraguay": ("🇵🇾", 31), "Peru": ("🇵🇪", 32), "Venezuela": ("🇻🇪", 33),
    "Bolivia": ("🇧🇴", 34), "Costa Rica": ("🇨🇷", 35), "Panama": ("🇵🇦", 36),
    "Honduras": ("🇭🇳", 37), "Jamaica": ("🇯🇲", 38), "El Salvador": ("🇸🇻", 39),
    "Ghana": ("🇬🇭", 40), "Nigeria": ("🇳🇬", 41), "Ivory Coast": ("🇨🇮", 42),
    "Cameroon": ("🇨🇲", 43), "Egypt": ("🇪🇬", 44), "Algeria": ("🇩🇿", 45),
    "Tunisia": ("🇹🇳", 46), "Saudi Arabia": ("🇸🇦", 47), "Iran": ("🇮🇷", 48),
    "Qatar": ("🇶🇦", 49), "Iraq": ("🇮🇶", 50), "South Africa": ("🇿🇦", 51),
    "New Zealand": ("🇳🇿", 52), "Ukraine": ("🇺🇦", 53), "Romania": ("🇷🇴", 54),
    "Slovakia": ("🇸🇰", 55), "Slovenia": ("🇸🇮", 56), "Greece": ("🇬🇷", 57),
    "Scotland": ("🏴󠁧󠁢󠁳󠁣󠁴󠁿", 58), "Czech Republic": ("🇨🇿", 59), "Czechia": ("🇨🇿", 59),
    "Wales": ("🏴󠁧󠁢󠁷󠁬󠁳󠁿", 60), "Albania": ("🇦🇱", 61), "Norway": ("🇳🇴", 62),
    "Sweden": ("🇸🇪", 63), "Finland": ("🇫🇮", 64),
}

_API_BASE = "https://api-football-v1.p.rapidapi.com/v3"
_WORLD_CUP_LEAGUE_ID = 1
_WORLD_CUP_SEASON = 2026

# ── Mock data (used when no API key or as fallback) ────────────────────────────

_MOCK_TEAMS: list[Team] = [
    Team(id=1,  name="Brazil",      flag="🇧🇷", fifa_rank=1),
    Team(id=2,  name="France",      flag="🇫🇷", fifa_rank=2),
    Team(id=3,  name="Argentina",   flag="🇦🇷", fifa_rank=3),
    Team(id=4,  name="Spain",       flag="🇪🇸", fifa_rank=4),
    Team(id=5,  name="England",     flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿", fifa_rank=5),
    Team(id=6,  name="Germany",     flag="🇩🇪", fifa_rank=6),
    Team(id=7,  name="Portugal",    flag="🇵🇹", fifa_rank=7),
    Team(id=8,  name="Netherlands", flag="🇳🇱", fifa_rank=8),
    Team(id=9,  name="Italy",       flag="🇮🇹", fifa_rank=9),
    Team(id=10, name="Croatia",     flag="🇭🇷", fifa_rank=10),
    Team(id=11, name="Uruguay",     flag="🇺🇾", fifa_rank=11),
    Team(id=12, name="Colombia",    flag="🇨🇴", fifa_rank=12),
    Team(id=13, name="Mexico",      flag="🇲🇽", fifa_rank=13),
    Team(id=14, name="USA",         flag="🇺🇸", fifa_rank=14),
    Team(id=15, name="Morocco",     flag="🇲🇦", fifa_rank=15),
    Team(id=16, name="Japan",       flag="🇯🇵", fifa_rank=16),
]
_MOCK_FIXTURES = [
    (1, 2, "Group A"), (3, 10, "Group B"), (6, 4, "Group C"), (9, 7, "Group D"),
    (5, 8, "Group E"), (11, 15, "Group F"), (14, 13, "Group G"), (12, 16, "Group H"),
]
_MOCK_TEAM_BY_ID = {t.id: t for t in _MOCK_TEAMS}
_KICKOFF_TIMES = ["12:00 EST", "15:00 EST", "18:00 EST", "21:00 EST"]


def _gen_odds(home_rank: int, away_rank: int) -> tuple[float, float, float]:
    rank_diff = away_rank - home_rank
    home_p = max(0.20, min(0.65, 0.35 + rank_diff * 0.02))
    draw_p = 0.27
    away_p = max(0.15, 1 - home_p - draw_p)
    total = home_p + draw_p + away_p
    margin = 1.08
    return (
        round(margin / (home_p / total), 2),
        round(margin / (draw_p / total), 2),
        round(margin / (away_p / total), 2),
    )


def _mock_upcoming_matches() -> list[Match]:
    base = date(2026, 7, 14)
    matches = []
    for idx, (home_id, away_id, group) in enumerate(_MOCK_FIXTURES):
        home = _MOCK_TEAM_BY_ID[home_id]
        away = _MOCK_TEAM_BY_ID[away_id]
        h, d, a = _gen_odds(home.fifa_rank, away.fifa_rank)
        matches.append(Match(
            id=idx + 1, home_team=home, away_team=away,
            kickoff_time=_KICKOFF_TIMES[idx % 4],
            kickoff_date=(base + timedelta(days=idx // 4)).isoformat(),
            group=group, home_odds=h, draw_odds=d, away_odds=a,
        ))
    return matches


def _mock_form(team: Team) -> list[FormResult]:
    rng = random.Random(team.id * 42)
    base = date(2026, 6, 1)
    results = []
    for i in range(5):
        opp = rng.choice(_MOCK_TEAMS)
        if opp.id == team.id:
            opp = _MOCK_TEAMS[(opp.id) % len(_MOCK_TEAMS)]
        diff = opp.fifa_rank - team.fifa_rank
        if diff > 2:
            sh, sa = rng.randint(1, 3), rng.randint(0, 1)
        elif diff < -2:
            sh, sa = rng.randint(0, 1), rng.randint(1, 3)
        else:
            sh, sa = rng.randint(0, 2), rng.randint(0, 2)
        result = "W" if sh > sa else ("D" if sh == sa else "L")
        results.append(FormResult(
            opponent=opp.name, opponent_flag=opp.flag,
            date=(base - timedelta(days=(i + 1) * 14)).isoformat(),
            score_home=sh, score_away=sa,
            result=result,  # type: ignore[arg-type]
            home_or_away="H" if i % 2 == 0 else "A",  # type: ignore[arg-type]
        ))
    return results


def _mock_h2h(home: Team, away: Team) -> list[H2HResult]:
    rng = random.Random((home.id + away.id) * 13)
    base = date(2026, 6, 1)
    results = []
    for i in range(5):
        diff = away.fifa_rank - home.fifa_rank
        if diff > 2:
            hg, ag = rng.randint(1, 3), rng.randint(0, 1)
        elif diff < -2:
            hg, ag = rng.randint(0, 1), rng.randint(1, 3)
        else:
            hg, ag = rng.randint(0, 2), rng.randint(0, 2)
        match_date = (base - timedelta(days=(i + 1) * 180)).isoformat()
        if i % 2 == 0:
            results.append(H2HResult(date=match_date, home_team=home.name, home_flag=home.flag,
                                     away_team=away.name, away_flag=away.flag,
                                     home_score=hg, away_score=ag))
        else:
            results.append(H2HResult(date=match_date, home_team=away.name, home_flag=away.flag,
                                     away_team=home.name, away_flag=home.flag,
                                     home_score=ag, away_score=hg))
    return results


def _mock_odds_comparison(match: Match) -> list[BookmakerOdds]:
    rng = random.Random(match.id * 77)
    bookmakers = ["Bet365", "William Hill", "Unibet", "Paddy Power"]
    return [
        BookmakerOdds(
            bookmaker=bm,
            home=round(match.home_odds + rng.uniform(-0.15, 0.15), 2),
            draw=round(match.draw_odds + rng.uniform(-0.10, 0.10), 2),
            away=round(match.away_odds + rng.uniform(-0.15, 0.15), 2),
        )
        for bm in bookmakers
    ]


# ── API-Football helpers ───────────────────────────────────────────────────────

def _api_headers() -> dict[str, str]:
    return {
        "X-RapidAPI-Key": settings.football_api_key,
        "X-RapidAPI-Host": settings.football_api_host,
    }


def _team_from_api(data: dict[str, Any]) -> Team:
    name = data["name"]
    api_id = data["id"]
    flag, rank = _TEAM_META.get(name, ("🏳️", 99))
    return Team(id=api_id, name=name, flag=flag, fifa_rank=rank, api_id=api_id)


def _kickoff_time_str(date_str: str) -> str:
    from datetime import datetime, timezone, timedelta as td
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        est = dt.astimezone(timezone(td(hours=-5)))
        return est.strftime("%H:%M EST")
    except Exception:
        return "TBD"


def _kickoff_date_str(date_str: str) -> str:
    return date_str[:10] if date_str else "TBD"


def _map_fixture_to_match(fixture: dict[str, Any], seq_id: int) -> Match:
    home_team = _team_from_api(fixture["teams"]["home"])
    away_team = _team_from_api(fixture["teams"]["away"])
    h, d, a = _gen_odds(home_team.fifa_rank, away_team.fifa_rank)
    return Match(
        id=seq_id,
        home_team=home_team,
        away_team=away_team,
        kickoff_time=_kickoff_time_str(fixture["fixture"]["date"]),
        kickoff_date=_kickoff_date_str(fixture["fixture"]["date"]),
        group=fixture["league"].get("round", "Group Stage"),
        home_odds=h, draw_odds=d, away_odds=a,
    )


def _map_fixture_to_form(fixture: dict[str, Any], team_api_id: int) -> FormResult:
    is_home = fixture["teams"]["home"]["id"] == team_api_id
    opp_data = fixture["teams"]["away"] if is_home else fixture["teams"]["home"]
    team_goals = (fixture["goals"]["home"] if is_home else fixture["goals"]["away"]) or 0
    opp_goals = (fixture["goals"]["away"] if is_home else fixture["goals"]["home"]) or 0
    winner = fixture["teams"]["home"]["winner"] if is_home else fixture["teams"]["away"]["winner"]
    result = "W" if winner is True else ("D" if winner is None else "L")
    opp_flag, _ = _TEAM_META.get(opp_data["name"], ("🏳️", 99))
    return FormResult(
        opponent=opp_data["name"], opponent_flag=opp_flag,
        date=_kickoff_date_str(fixture["fixture"]["date"]),
        score_home=team_goals, score_away=opp_goals,
        result=result,  # type: ignore[arg-type]
        home_or_away="H" if is_home else "A",  # type: ignore[arg-type]
    )


def _map_fixture_to_h2h(fixture: dict[str, Any]) -> H2HResult:
    home_name = fixture["teams"]["home"]["name"]
    away_name = fixture["teams"]["away"]["name"]
    home_flag, _ = _TEAM_META.get(home_name, ("🏳️", 99))
    away_flag, _ = _TEAM_META.get(away_name, ("🏳️", 99))
    return H2HResult(
        date=_kickoff_date_str(fixture["fixture"]["date"]),
        home_team=home_name, home_flag=home_flag,
        away_team=away_name, away_flag=away_flag,
        home_score=(fixture["goals"]["home"] or 0),
        away_score=(fixture["goals"]["away"] or 0),
    )


async def _fetch_upcoming_fixtures() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_API_BASE}/fixtures",
            headers=_api_headers(),
            params={"league": _WORLD_CUP_LEAGUE_ID, "season": _WORLD_CUP_SEASON,
                    "status": "NS", "next": 50},
        )
        r.raise_for_status()
        return r.json().get("response", [])


async def _fetch_team_form(team_api_id: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_API_BASE}/fixtures",
            headers=_api_headers(),
            params={"team": team_api_id, "last": 5},
        )
        r.raise_for_status()
        return r.json().get("response", [])


async def _fetch_h2h(team1_api_id: int, team2_api_id: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_API_BASE}/fixtures/headtohead",
            headers=_api_headers(),
            params={"h2h": f"{team1_api_id}-{team2_api_id}", "last": 5},
        )
        r.raise_for_status()
        return r.json().get("response", [])


# ── Public async API ───────────────────────────────────────────────────────────

async def get_upcoming_matches() -> list[Match]:
    if not settings.football_api_key:
        return _mock_upcoming_matches()
    try:
        fixtures = await _fetch_upcoming_fixtures()
        if not fixtures:
            return _mock_upcoming_matches()
        return [_map_fixture_to_match(f, idx + 1) for idx, f in enumerate(fixtures)]
    except Exception:
        return _mock_upcoming_matches()


async def get_match_detail(fixture_id: int) -> MatchDetail | None:
    matches = await get_upcoming_matches()
    match = next((m for m in matches if m.id == fixture_id), None)
    if match is None:
        return None

    if not settings.football_api_key or match.home_team.api_id == 0:
        return MatchDetail(
            match=match,
            home_form=_mock_form(match.home_team),
            away_form=_mock_form(match.away_team),
            h2h=_mock_h2h(match.home_team, match.away_team),
            odds_comparison=_mock_odds_comparison(match),
        )

    try:
        home_raw, away_raw, h2h_raw = await asyncio.gather(
            _fetch_team_form(match.home_team.api_id),
            _fetch_team_form(match.away_team.api_id),
            _fetch_h2h(match.home_team.api_id, match.away_team.api_id),
        )
        home_form = [_map_fixture_to_form(f, match.home_team.api_id) for f in home_raw[:5]]
        away_form = [_map_fixture_to_form(f, match.away_team.api_id) for f in away_raw[:5]]
        h2h = [_map_fixture_to_h2h(f) for f in h2h_raw[:5]]
        return MatchDetail(
            match=match,
            home_form=home_form or _mock_form(match.home_team),
            away_form=away_form or _mock_form(match.away_team),
            h2h=h2h or _mock_h2h(match.home_team, match.away_team),
            odds_comparison=_mock_odds_comparison(match),
        )
    except Exception:
        return MatchDetail(
            match=match,
            home_form=_mock_form(match.home_team),
            away_form=_mock_form(match.away_team),
            h2h=_mock_h2h(match.home_team, match.away_team),
            odds_comparison=_mock_odds_comparison(match),
        )
