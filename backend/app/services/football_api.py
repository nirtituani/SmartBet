import random
from datetime import date, timedelta

from app.models.match import (
    BookmakerOdds, FormResult, H2HResult, Match, MatchDetail, Team,
)

TEAMS: list[Team] = [
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

_KICKOFF_TIMES = ["12:00 EST", "15:00 EST", "18:00 EST", "21:00 EST"]
_FIXTURES = [
    (1,  2,  "Group A"),
    (3,  10, "Group B"),
    (6,  4,  "Group C"),
    (9,  7,  "Group D"),
    (5,  8,  "Group E"),
    (11, 15, "Group F"),
    (14, 13, "Group G"),
    (12, 16, "Group H"),
]
_TEAM_BY_ID = {t.id: t for t in TEAMS}


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


def get_upcoming_matches() -> list[Match]:
    base = date(2026, 7, 14)
    matches = []
    for idx, (home_id, away_id, group) in enumerate(_FIXTURES):
        home = _TEAM_BY_ID[home_id]
        away = _TEAM_BY_ID[away_id]
        h, d, a = _gen_odds(home.fifa_rank, away.fifa_rank)
        matches.append(Match(
            id=idx + 1,
            home_team=home,
            away_team=away,
            kickoff_time=_KICKOFF_TIMES[idx % 4],
            kickoff_date=(base + timedelta(days=idx // 4)).isoformat(),
            group=group,
            home_odds=h,
            draw_odds=d,
            away_odds=a,
        ))
    return matches


def _get_form(team: Team) -> list[FormResult]:
    rng = random.Random(team.id * 42)
    opponents = [t for t in TEAMS if t.id != team.id]
    base = date(2026, 6, 1)
    results = []
    for i in range(5):
        opp = rng.choice(opponents)
        diff = opp.fifa_rank - team.fifa_rank
        if diff > 2:
            sh, sa = rng.randint(1, 3), rng.randint(0, 1)
        elif diff < -2:
            sh, sa = rng.randint(0, 1), rng.randint(1, 3)
        else:
            sh, sa = rng.randint(0, 2), rng.randint(0, 2)
        result: str = "W" if sh > sa else ("D" if sh == sa else "L")
        results.append(FormResult(
            opponent=opp.name,
            opponent_flag=opp.flag,
            date=(base - timedelta(days=(i + 1) * 14)).isoformat(),
            score_home=sh,
            score_away=sa,
            result=result,  # type: ignore[arg-type]
            home_or_away="H" if i % 2 == 0 else "A",  # type: ignore[arg-type]
        ))
    return results


def _get_h2h(home: Team, away: Team) -> list[H2HResult]:
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


def _get_odds_comparison(match: Match) -> list[BookmakerOdds]:
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


def get_match_detail(fixture_id: int) -> MatchDetail | None:
    matches = get_upcoming_matches()
    match = next((m for m in matches if m.id == fixture_id), None)
    if match is None:
        return None
    return MatchDetail(
        match=match,
        home_form=_get_form(match.home_team),
        away_form=_get_form(match.away_team),
        h2h=_get_h2h(match.home_team, match.away_team),
        odds_comparison=_get_odds_comparison(match),
    )
