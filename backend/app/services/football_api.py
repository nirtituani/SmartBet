import asyncio
import random
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import settings
from app.models.match import (
    BookmakerOdds, FormResult, H2HResult, Match, MatchDetail, MatchLineup, Player, ScoreOdd, StandingRow, Team, TeamLineup,
)

# ── Static meta (flag emoji + approximate FIFA rank) ──────────────────────────

_TEAM_META: dict[str, tuple[str, int]] = {
    # WC 2026 teams — FIFA rankings as of April 2026
    "France": ("🇫🇷", 1), "Spain": ("🇪🇸", 2), "Argentina": ("🇦🇷", 3),
    "England": ("🏴󠁧󠁢󠁥󠁮󠁧󠁿", 4), "Portugal": ("🇵🇹", 5), "Brazil": ("🇧🇷", 6),
    "Netherlands": ("🇳🇱", 7), "Morocco": ("🇲🇦", 8), "Belgium": ("🇧🇪", 9),
    "Germany": ("🇩🇪", 10), "Croatia": ("🇭🇷", 11), "Colombia": ("🇨🇴", 13),
    "Senegal": ("🇸🇳", 14), "Mexico": ("🇲🇽", 15), "USA": ("🇺🇸", 16),
    "Uruguay": ("🇺🇾", 17), "Japan": ("🇯🇵", 18), "Switzerland": ("🇨🇭", 19),
    "Iran": ("🇮🇷", 21), "Turkey": ("🇹🇷", 22), "Ecuador": ("🇪🇨", 23),
    "Austria": ("🇦🇹", 24), "South Korea": ("🇰🇷", 25), "Australia": ("🇦🇺", 27),
    "Algeria": ("🇩🇿", 28), "Egypt": ("🇪🇬", 29), "Canada": ("🇨🇦", 30),
    "Norway": ("🇳🇴", 31), "Panama": ("🇵🇦", 33), "Ivory Coast": ("🇨🇮", 34),
    "Sweden": ("🇸🇪", 38), "Paraguay": ("🇵🇾", 40), "Czechia": ("🇨🇿", 41),
    "Scotland": ("🏴󠁧󠁢󠁳󠁣󠁴󠁿", 43), "Tunisia": ("🇹🇳", 44), "DR Congo": ("🇨🇩", 46),
    "Uzbekistan": ("🇺🇿", 50), "Qatar": ("🇶🇦", 55), "Iraq": ("🇮🇶", 57),
    "South Africa": ("🇿🇦", 60), "Saudi Arabia": ("🇸🇦", 61), "Jordan": ("🇯🇴", 63),
    "Bosnia & Herzegovina": ("🇧🇦", 65), "Ghana": ("🇬🇭", 74),
    "Curacao": ("🇨🇼", 82), "Haiti": ("🇭🇹", 83), "New Zealand": ("🇳🇿", 85),
    "Cape Verde": ("🇨🇻", 69),
    # Aliases
    "Czech Republic": ("🇨🇿", 41),
    # Non-WC teams that appear as form/H2H opponents
    "Italy": ("🇮🇹", 12), "Denmark": ("🇩🇰", 20), "Nigeria": ("🇳🇬", 26),
    "Ukraine": ("🇺🇦", 32), "Poland": ("🇵🇱", 35), "Serbia": ("🇷🇸", 39),
    "Venezuela": ("🇻🇪", 49), "Chile": ("🇨🇱", 54), "Romania": ("🇷🇴", 56),
    "Slovenia": ("🇸🇮", 58), "Hungary": ("🇭🇺", 42), "Greece": ("🇬🇷", 47),
    "Slovakia": ("🇸🇰", 48), "Peru": ("🇵🇪", 53), "Bolivia": ("🇧🇴", 76),
    "Costa Rica": ("🇨🇷", 51), "Honduras": ("🇭🇳", 66), "Jamaica": ("🇯🇲", 71),
    "El Salvador": ("🇸🇻", 100), "Cameroon": ("🇨🇲", 45), "Wales": ("🏴󠁧󠁢󠁷󠁬󠁳󠁿", 37),
    "Albania": ("🇦🇱", 64), "Finland": ("🇫🇮", 73), "Georgia": ("🇬🇪", 72),
    "Azerbaijan": ("🇦🇿", 124), "Iceland": ("🇮🇸", 75), "Burundi": ("🇧🇮", 142),
    "Zambia": ("🇿🇲", 92), "Tanzania": ("🇹🇿", 113), "Lesotho": ("🇱🇸", 145),
    "Paraguay": ("🇵🇾", 40),
}

_API_BASE = "https://api-football-v1.p.rapidapi.com/v3"
_WORLD_CUP_LEAGUE_ID = 1
_WORLD_CUP_SEASON = 2026
_WC26_BASE = "https://wc26-live-football-api.p.rapidapi.com"

# ── Real WC 2026 fixture schedule (embedded, no API needed) ───────────────────

_WC26_FIXTURES: list[dict] = [
    # GROUP A
    {"id": 1,  "home": "Mexico",      "away": "South Africa",      "date": "2026-06-11", "time": "15:00 ET", "group": "Group A", "venue": "Mexico City"},
    {"id": 2,  "home": "South Korea", "away": "Czechia",           "date": "2026-06-11", "time": "22:00 ET", "group": "Group A", "venue": "Zapopan"},
    {"id": 3,  "home": "Czechia",     "away": "South Africa",      "date": "2026-06-18", "time": "12:00 ET", "group": "Group A", "venue": "Atlanta"},
    {"id": 4,  "home": "Mexico",      "away": "South Korea",       "date": "2026-06-18", "time": "21:00 ET", "group": "Group A", "venue": "Zapopan"},
    {"id": 5,  "home": "Czechia",     "away": "Mexico",            "date": "2026-06-24", "time": "21:00 ET", "group": "Group A", "venue": "Mexico City"},
    {"id": 6,  "home": "South Africa","away": "South Korea",       "date": "2026-06-24", "time": "21:00 ET", "group": "Group A", "venue": "Monterrey"},
    # GROUP B
    {"id": 7,  "home": "Canada",      "away": "Bosnia & Herzegovina","date": "2026-06-12","time": "15:00 ET","group": "Group B", "venue": "Toronto"},
    {"id": 8,  "home": "Qatar",       "away": "Switzerland",       "date": "2026-06-13", "time": "15:00 ET", "group": "Group B", "venue": "Santa Clara"},
    {"id": 9,  "home": "Switzerland", "away": "Bosnia & Herzegovina","date": "2026-06-18","time": "15:00 ET","group": "Group B", "venue": "Los Angeles"},
    {"id": 10, "home": "Canada",      "away": "Qatar",             "date": "2026-06-18", "time": "18:00 ET", "group": "Group B", "venue": "Vancouver"},
    {"id": 11, "home": "Switzerland", "away": "Canada",            "date": "2026-06-24", "time": "15:00 ET", "group": "Group B", "venue": "Vancouver"},
    {"id": 12, "home": "Bosnia & Herzegovina","away": "Qatar",     "date": "2026-06-24", "time": "15:00 ET", "group": "Group B", "venue": "Seattle"},
    # GROUP C
    {"id": 13, "home": "Brazil",      "away": "Morocco",           "date": "2026-06-13", "time": "18:00 ET", "group": "Group C", "venue": "New York/NJ"},
    {"id": 14, "home": "Haiti",       "away": "Scotland",          "date": "2026-06-13", "time": "21:00 ET", "group": "Group C", "venue": "Boston"},
    {"id": 15, "home": "Scotland",    "away": "Morocco",           "date": "2026-06-19", "time": "18:00 ET", "group": "Group C", "venue": "Boston"},
    {"id": 16, "home": "Brazil",      "away": "Haiti",             "date": "2026-06-19", "time": "20:30 ET", "group": "Group C", "venue": "Philadelphia"},
    {"id": 17, "home": "Scotland",    "away": "Brazil",            "date": "2026-06-24", "time": "18:00 ET", "group": "Group C", "venue": "Miami"},
    {"id": 18, "home": "Morocco",     "away": "Haiti",             "date": "2026-06-24", "time": "18:00 ET", "group": "Group C", "venue": "Atlanta"},
    # GROUP D
    {"id": 19, "home": "USA",         "away": "Paraguay",          "date": "2026-06-12", "time": "21:00 ET", "group": "Group D", "venue": "Los Angeles"},
    {"id": 20, "home": "Australia",   "away": "Turkey",            "date": "2026-06-14", "time": "00:00 ET", "group": "Group D", "venue": "Vancouver"},
    {"id": 21, "home": "USA",         "away": "Australia",         "date": "2026-06-19", "time": "15:00 ET", "group": "Group D", "venue": "Seattle"},
    {"id": 22, "home": "Turkey",      "away": "Paraguay",          "date": "2026-06-20", "time": "00:00 ET", "group": "Group D", "venue": "Santa Clara"},
    {"id": 23, "home": "Turkey",      "away": "USA",               "date": "2026-06-25", "time": "22:00 ET", "group": "Group D", "venue": "Los Angeles"},
    {"id": 24, "home": "Paraguay",    "away": "Australia",         "date": "2026-06-25", "time": "22:00 ET", "group": "Group D", "venue": "Santa Clara"},
    # GROUP E
    {"id": 25, "home": "Germany",     "away": "Curacao",           "date": "2026-06-14", "time": "13:00 ET", "group": "Group E", "venue": "Houston"},
    {"id": 26, "home": "Ivory Coast", "away": "Ecuador",           "date": "2026-06-14", "time": "19:00 ET", "group": "Group E", "venue": "Philadelphia"},
    {"id": 27, "home": "Germany",     "away": "Ivory Coast",       "date": "2026-06-20", "time": "16:00 ET", "group": "Group E", "venue": "Toronto"},
    {"id": 28, "home": "Ecuador",     "away": "Curacao",           "date": "2026-06-20", "time": "20:00 ET", "group": "Group E", "venue": "Kansas City"},
    {"id": 29, "home": "Curacao",     "away": "Ivory Coast",       "date": "2026-06-25", "time": "16:00 ET", "group": "Group E", "venue": "Philadelphia"},
    {"id": 30, "home": "Ecuador",     "away": "Germany",           "date": "2026-06-25", "time": "16:00 ET", "group": "Group E", "venue": "New York/NJ"},
    # GROUP F
    {"id": 31, "home": "Netherlands", "away": "Japan",             "date": "2026-06-14", "time": "16:00 ET", "group": "Group F", "venue": "Dallas"},
    {"id": 32, "home": "Sweden",      "away": "Tunisia",           "date": "2026-06-14", "time": "22:00 ET", "group": "Group F", "venue": "Monterrey"},
    {"id": 33, "home": "Netherlands", "away": "Sweden",            "date": "2026-06-20", "time": "13:00 ET", "group": "Group F", "venue": "Houston"},
    {"id": 34, "home": "Tunisia",     "away": "Japan",             "date": "2026-06-21", "time": "00:00 ET", "group": "Group F", "venue": "Monterrey"},
    {"id": 35, "home": "Japan",       "away": "Sweden",            "date": "2026-06-25", "time": "19:00 ET", "group": "Group F", "venue": "Dallas"},
    {"id": 36, "home": "Tunisia",     "away": "Netherlands",       "date": "2026-06-25", "time": "19:00 ET", "group": "Group F", "venue": "Kansas City"},
    # GROUP G
    {"id": 37, "home": "Belgium",     "away": "Egypt",             "date": "2026-06-15", "time": "15:00 ET", "group": "Group G", "venue": "Seattle"},
    {"id": 38, "home": "Iran",        "away": "New Zealand",       "date": "2026-06-15", "time": "21:00 ET", "group": "Group G", "venue": "Los Angeles"},
    {"id": 39, "home": "Belgium",     "away": "Iran",              "date": "2026-06-21", "time": "15:00 ET", "group": "Group G", "venue": "Los Angeles"},
    {"id": 40, "home": "New Zealand", "away": "Egypt",             "date": "2026-06-21", "time": "21:00 ET", "group": "Group G", "venue": "Vancouver"},
    {"id": 41, "home": "Egypt",       "away": "Iran",              "date": "2026-06-26", "time": "23:00 ET", "group": "Group G", "venue": "Seattle"},
    {"id": 42, "home": "New Zealand", "away": "Belgium",           "date": "2026-06-26", "time": "23:00 ET", "group": "Group G", "venue": "Vancouver"},
    # GROUP H
    {"id": 43, "home": "Spain",       "away": "Cape Verde",        "date": "2026-06-15", "time": "12:00 ET", "group": "Group H", "venue": "Atlanta"},
    {"id": 44, "home": "Saudi Arabia","away": "Uruguay",           "date": "2026-06-15", "time": "18:00 ET", "group": "Group H", "venue": "Miami"},
    {"id": 45, "home": "Spain",       "away": "Saudi Arabia",      "date": "2026-06-21", "time": "12:00 ET", "group": "Group H", "venue": "Atlanta"},
    {"id": 46, "home": "Uruguay",     "away": "Cape Verde",        "date": "2026-06-21", "time": "18:00 ET", "group": "Group H", "venue": "Miami"},
    {"id": 47, "home": "Cape Verde",  "away": "Saudi Arabia",      "date": "2026-06-26", "time": "20:00 ET", "group": "Group H", "venue": "Houston"},
    {"id": 48, "home": "Uruguay",     "away": "Spain",             "date": "2026-06-26", "time": "20:00 ET", "group": "Group H", "venue": "Zapopan"},
    # GROUP I
    {"id": 49, "home": "France",      "away": "Senegal",           "date": "2026-06-16", "time": "15:00 ET", "group": "Group I", "venue": "New York/NJ"},
    {"id": 50, "home": "Iraq",        "away": "Norway",            "date": "2026-06-16", "time": "18:00 ET", "group": "Group I", "venue": "Boston"},
    {"id": 51, "home": "France",      "away": "Iraq",              "date": "2026-06-22", "time": "17:00 ET", "group": "Group I", "venue": "Philadelphia"},
    {"id": 52, "home": "Norway",      "away": "Senegal",           "date": "2026-06-22", "time": "20:00 ET", "group": "Group I", "venue": "New York/NJ"},
    {"id": 53, "home": "Norway",      "away": "France",            "date": "2026-06-26", "time": "15:00 ET", "group": "Group I", "venue": "Boston"},
    {"id": 54, "home": "Senegal",     "away": "Iraq",              "date": "2026-06-26", "time": "15:00 ET", "group": "Group I", "venue": "Toronto"},
    # GROUP J
    {"id": 55, "home": "Argentina",   "away": "Algeria",           "date": "2026-06-16", "time": "21:00 ET", "group": "Group J", "venue": "Kansas City"},
    {"id": 56, "home": "Austria",     "away": "Jordan",            "date": "2026-06-17", "time": "00:00 ET", "group": "Group J", "venue": "Santa Clara"},
    {"id": 57, "home": "Argentina",   "away": "Austria",           "date": "2026-06-22", "time": "13:00 ET", "group": "Group J", "venue": "Dallas"},
    {"id": 58, "home": "Jordan",      "away": "Algeria",           "date": "2026-06-22", "time": "23:00 ET", "group": "Group J", "venue": "Santa Clara"},
    {"id": 59, "home": "Algeria",     "away": "Austria",           "date": "2026-06-27", "time": "22:00 ET", "group": "Group J", "venue": "Kansas City"},
    {"id": 60, "home": "Jordan",      "away": "Argentina",         "date": "2026-06-27", "time": "22:00 ET", "group": "Group J", "venue": "Dallas"},
    # GROUP K
    {"id": 61, "home": "Portugal",    "away": "DR Congo",          "date": "2026-06-17", "time": "13:00 ET", "group": "Group K", "venue": "Houston"},
    {"id": 62, "home": "Uzbekistan",  "away": "Colombia",          "date": "2026-06-17", "time": "22:00 ET", "group": "Group K", "venue": "Mexico City"},
    {"id": 63, "home": "Portugal",    "away": "Uzbekistan",        "date": "2026-06-23", "time": "13:00 ET", "group": "Group K", "venue": "Houston"},
    {"id": 64, "home": "Colombia",    "away": "DR Congo",          "date": "2026-06-23", "time": "22:00 ET", "group": "Group K", "venue": "Zapopan"},
    {"id": 65, "home": "Colombia",    "away": "Portugal",          "date": "2026-06-27", "time": "19:30 ET", "group": "Group K", "venue": "Miami"},
    {"id": 66, "home": "DR Congo",    "away": "Uzbekistan",        "date": "2026-06-27", "time": "19:30 ET", "group": "Group K", "venue": "Atlanta"},
    # GROUP L
    {"id": 67, "home": "England",     "away": "Croatia",           "date": "2026-06-17", "time": "16:00 ET", "group": "Group L", "venue": "Dallas"},
    {"id": 68, "home": "Ghana",       "away": "Panama",            "date": "2026-06-17", "time": "19:00 ET", "group": "Group L", "venue": "Toronto"},
    {"id": 69, "home": "England",     "away": "Ghana",             "date": "2026-06-23", "time": "16:00 ET", "group": "Group L", "venue": "Boston"},
    {"id": 70, "home": "Panama",      "away": "Croatia",           "date": "2026-06-23", "time": "19:00 ET", "group": "Group L", "venue": "Toronto"},
    {"id": 71, "home": "Panama",      "away": "England",           "date": "2026-06-27", "time": "17:00 ET", "group": "Group L", "venue": "New York/NJ"},
    {"id": 72, "home": "Croatia",     "away": "Ghana",             "date": "2026-06-27", "time": "17:00 ET", "group": "Group L", "venue": "Philadelphia"},
]

_KICKOFF_TIMES = ["12:00 EST", "15:00 EST", "18:00 EST", "21:00 EST"]

# team name → group name (precomputed from fixture list)
_TEAM_TO_GROUP: dict[str, str] = {
    f[side]: f["group"]
    for f in _WC26_FIXTURES
    for side in ("home", "away")
}


async def _fetch_wc_results() -> list[dict]:
    """Fetch all finished WC 2026 group stage matches from API-Football."""
    if not settings.football_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{_API_BASE}/fixtures",
                headers=_api_headers(),
                params={"league": _WORLD_CUP_LEAGUE_ID, "season": _WORLD_CUP_SEASON},
            )
            r.raise_for_status()
        finished = {"FT", "AET", "PEN"}
        return [
            f for f in r.json().get("response", [])
            if f.get("fixture", {}).get("status", {}).get("short") in finished
        ]
    except Exception:
        return []


def _init_groups() -> dict[str, dict[str, StandingRow]]:
    groups: dict[str, dict[str, StandingRow]] = {}
    for f in _WC26_FIXTURES:
        g = f["group"]
        if g not in groups:
            groups[g] = {}
        for side in ("home", "away"):
            name = f[side]
            if name not in groups[g]:
                flag, rank = _TEAM_META.get(name, ("🏳️", 99))
                groups[g][name] = StandingRow(
                    name=name, flag=flag, fifa_rank=rank,
                    mp=0, w=0, d=0, l=0, gf=0, ga=0, gd=0, pts=0,
                )
    return groups


def _apply_result(
    groups: dict[str, dict[str, StandingRow]],
    hname: str, aname: str, hg: int, ag: int,
    group_results: dict[str, list[tuple[str, str, int, int]]] | None = None,
) -> None:
    grp = _TEAM_TO_GROUP.get(hname)
    if not grp or hname not in groups.get(grp, {}) or aname not in groups.get(grp, {}):
        return
    h, a = groups[grp][hname], groups[grp][aname]
    h.mp += 1; a.mp += 1
    h.gf += hg; h.ga += ag; h.gd = h.gf - h.ga
    a.gf += ag; a.ga += hg; a.gd = a.gf - a.ga
    if hg > ag:
        h.w += 1; h.pts += 3; a.l += 1
    elif ag > hg:
        a.w += 1; a.pts += 3; h.l += 1
    else:
        h.d += 1; h.pts += 1; a.d += 1; a.pts += 1
    if group_results is not None:
        group_results.setdefault(grp, []).append((hname, aname, hg, ag))


def _h2h_sort(
    rows: list[StandingRow],
    results: list[tuple[str, str, int, int]],
) -> list[StandingRow]:
    """Recursively sort tied-on-pts teams by H2H criteria.

    Order: H2H pts → H2H GD → H2H GF → (reapply H2H to still-tied subset)
           → overall GD → overall GF → FIFA rank.
    """
    if len(rows) <= 1:
        return rows

    names = {t.name for t in rows}

    def h2h_stats(name: str) -> tuple[int, int, int]:
        pts = gd = gf = 0
        for h, a, hg, ag in results:
            if h == name and a in names and a != name:
                pts += 3 if hg > ag else (1 if hg == ag else 0)
                gd += hg - ag; gf += hg
            elif a == name and h in names and h != name:
                pts += 3 if ag > hg else (1 if ag == hg else 0)
                gd += ag - hg; gf += ag
        return (-pts, -gd, -gf)

    sorted_rows = sorted(rows, key=lambda t: (*h2h_stats(t.name), t.fifa_rank))

    out: list[StandingRow] = []
    i = 0
    while i < len(sorted_rows):
        j = i + 1
        key_i = h2h_stats(sorted_rows[i].name)
        while j < len(sorted_rows) and h2h_stats(sorted_rows[j].name) == key_i:
            j += 1
        sub = sorted_rows[i:j]
        if len(sub) > 1:
            if len(sub) < len(rows):
                # Subset is smaller: re-apply H2H exclusively to these teams
                sub = _h2h_sort(sub, results)
            else:
                # H2H made no progress at all: fall through to overall GD → GF → fair play → FIFA rank
                sub = sorted(sub, key=lambda t: (-t.gd, -t.gf, -t.fair_play, t.fifa_rank))
        out.extend(sub)
        i = j
    return out


def _sort_group_rows(
    rows: list[StandingRow],
    results: list[tuple[str, str, int, int]],
) -> list[StandingRow]:
    """FIFA WC 2026 tiebreaker: pts → H2H(pts,GD,GF,recursive) → overall GD → overall GF → FIFA rank."""
    by_pts = sorted(rows, key=lambda t: (-t.pts, t.fifa_rank))
    out: list[StandingRow] = []
    i = 0
    while i < len(by_pts):
        j = i + 1
        while j < len(by_pts) and by_pts[j].pts == by_pts[i].pts:
            j += 1
        tied = by_pts[i:j]
        if len(tied) > 1:
            tied = _h2h_sort(tied, results)
        out.extend(tied)
        i = j
    return out


def _sort_groups(
    groups: dict[str, dict[str, StandingRow]],
    group_results: dict[str, list[tuple[str, str, int, int]]] | None = None,
) -> dict[str, list[StandingRow]]:
    return {
        g: _sort_group_rows(list(teams.values()), (group_results or {}).get(g, []))
        for g, teams in sorted(groups.items())
    }


def calculate_group_standings(results: list[dict]) -> dict[str, list[StandingRow]]:
    """Build group standings from API-Football finished match results."""
    groups = _init_groups()
    group_results: dict[str, list[tuple[str, str, int, int]]] = {}
    for match in results:
        hname = _AF_NAME_MAP.get(match["teams"]["home"]["name"], match["teams"]["home"]["name"])
        aname = _AF_NAME_MAP.get(match["teams"]["away"]["name"], match["teams"]["away"]["name"])
        hg = match["goals"].get("home") or 0
        ag = match["goals"].get("away") or 0
        _apply_result(groups, hname, aname, hg, ag, group_results)
    return _sort_groups(groups, group_results)


_GROUP_STAGE_START = "20260612"
_GROUP_STAGE_END   = "20260702"

# Maps ESPN displayName → our internal name (superset of _ESPN_MATCH_NAME_MAP)
_ESPN_STANDINGS_NAME_MAP: dict[str, str] = {
    **{k: v for k, v in {
        "Bosnia-Herzegovina": "Bosnia & Herzegovina",
        "Bosnia-Herz": "Bosnia & Herzegovina",
        "Congo DR": "DR Congo",
        "Türkiye": "Turkey",
        "United States": "USA",
        "IR Iran": "Iran",
        "Korea Republic": "South Korea",
        "Côte d'Ivoire": "Ivory Coast",
        "Curaçao": "Curacao",
    }.items()},
}


_ESPN_SUMMARY = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary"

# FIFA fair play deductions per card type
_CARD_DEDUCTIONS = {"yellow-card": 1, "yellow-red-card": 3, "red-card": 4}


async def _fetch_match_fair_play(client: httpx.AsyncClient, event_id: str) -> dict[str, int]:
    """Return {team_name: fair_play_points} for one completed match.
    Applies FIFA rule: only one deduction per player per match.
    Cached in Redis for 7 days (result never changes).
    """
    from app.core.cache import get_cached, set_cached
    cache_key = f"espn_cards_v1:{event_id}"
    cached = await get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        resp = await client.get(_ESPN_SUMMARY, params={"event": event_id}, timeout=10.0)
        data = resp.json()
    except Exception:
        return {}

    # Per player: collect card events so we can apply the "one deduction" rule
    from collections import defaultdict
    player_cards: dict[tuple[str, str], list[str]] = defaultdict(list)
    for event in data.get("keyEvents", []):
        etype = event.get("type", {}).get("type", "")
        if etype not in _CARD_DEDUCTIONS:
            continue
        raw = event.get("team", {}).get("displayName", "")
        team = _ESPN_STANDINGS_NAME_MAP.get(raw, raw)
        participants = event.get("participants", [])
        pid = participants[0].get("athlete", {}).get("id", "unk") if participants else "unk"
        player_cards[(team, pid)].append(etype)

    result: dict[str, int] = {}
    for (team, _), cards in player_cards.items():
        if "yellow-red-card" in cards:
            # Second yellow: only -3 (the first yellow is NOT counted separately)
            deduction = 3
        elif "red-card" in cards and "yellow-card" in cards:
            deduction = 5  # yellow + direct red
        elif "red-card" in cards:
            deduction = 4  # direct red only
        else:
            deduction = cards.count("yellow-card")  # plain yellow(s): -1 each
        result[team] = result.get(team, 0) - deduction

    await set_cached(cache_key, result, ttl=7 * 24 * 3600)
    return result


async def fetch_group_standings() -> dict[str, list[StandingRow]]:
    """Calculate group standings from ESPN scoreboard + per-match card data."""
    from datetime import date, timedelta
    today = date.today()
    end = min(today, date(2026, 7, 2))
    start = date(2026, 6, 11)

    dates = []
    d = start
    while d <= end:
        dates.append(d.strftime("%Y%m%d"))
        d += timedelta(days=1)

    groups = _init_groups()
    group_results: dict[str, list[tuple[str, str, int, int]]] = {}
    completed_event_ids: list[str] = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: fetch all scoreboard dates to get scores + event IDs
            score_responses = await asyncio.gather(
                *[client.get(_ESPN_SCOREBOARD, params={"dates": dt}) for dt in dates],
                return_exceptions=True,
            )
            for resp in score_responses:
                if isinstance(resp, Exception):
                    continue
                try:
                    data = resp.json()
                except Exception:
                    continue
                for event in data.get("events", []):
                    comp = (event.get("competitions") or [{}])[0]
                    if not comp.get("status", {}).get("type", {}).get("completed", False):
                        continue
                    competitors = comp.get("competitors", [])
                    if len(competitors) != 2:
                        continue
                    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
                    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
                    if not home or not away:
                        continue
                    hraw = home.get("team", {}).get("displayName", "")
                    araw = away.get("team", {}).get("displayName", "")
                    hname = _ESPN_STANDINGS_NAME_MAP.get(hraw, hraw)
                    aname = _ESPN_STANDINGS_NAME_MAP.get(araw, araw)
                    try:
                        hg = int(home.get("score") or 0)
                        ag = int(away.get("score") or 0)
                    except (ValueError, TypeError):
                        continue
                    _apply_result(groups, hname, aname, hg, ag, group_results)
                    if event.get("id"):
                        completed_event_ids.append(str(event["id"]))

            # Step 2: fetch card data for all completed matches (cached per match)
            fair_play: dict[str, int] = {}
            card_results = await asyncio.gather(
                *[_fetch_match_fair_play(client, eid) for eid in completed_event_ids],
                return_exceptions=True,
            )
            for fp in card_results:
                if isinstance(fp, dict):
                    for team, pts in fp.items():
                        fair_play[team] = fair_play.get(team, 0) + pts

            # Apply fair play to each StandingRow
            for grp_teams in groups.values():
                for name, row in grp_teams.items():
                    row.fair_play = fair_play.get(name, 0)

    except Exception:
        pass

    return _sort_groups(groups, group_results)


# ── ESPN team IDs for all 48 WC 2026 teams ────────────────────────────────────
_ESPN_TEAM_IDS: dict[str, int] = {
    "Algeria": 624, "Argentina": 202, "Australia": 628, "Austria": 474,
    "Belgium": 459, "Bosnia & Herzegovina": 452, "Brazil": 205, "Canada": 206,
    "Cape Verde": 2597, "Colombia": 208, "DR Congo": 2850, "Croatia": 477,
    "Curacao": 11678, "Czechia": 450, "Ecuador": 209, "Egypt": 2620,
    "England": 448, "France": 478, "Germany": 481, "Ghana": 4469,
    "Haiti": 2654, "Iran": 469, "Iraq": 4375, "Ivory Coast": 4789,
    "Japan": 627, "Jordan": 2917, "Mexico": 203, "Morocco": 2869,
    "Netherlands": 449, "New Zealand": 2666, "Norway": 464, "Panama": 2659,
    "Paraguay": 210, "Portugal": 482, "Qatar": 4398, "Saudi Arabia": 655,
    "Scotland": 580, "Senegal": 654, "South Africa": 467, "South Korea": 451,
    "Spain": 164, "Sweden": 466, "Switzerland": 475, "Tunisia": 659,
    "Turkey": 465, "USA": 660, "Uruguay": 212, "Uzbekistan": 2570,
}
_ESPN_NAME_MAP: dict[str, str] = {
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "Congo DR": "DR Congo",
    "Türkiye": "Turkey",
    "United States": "USA",
}
_ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams"

# ── SofaScore (unofficial, no key needed) ────────────────────────────────────
_SOFASCORE_BASE = "https://api.sofascore.com/api/v1"
_SOFASCORE_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SmartBet/1.0)"}

# Our name → SofaScore variations (lowercase)
_SOFASCORE_ALIASES: dict[str, list[str]] = {
    "USA": ["united states", "usa"],
    "Bosnia & Herzegovina": ["bosnia & herzegovina", "bosnia-herzegovina", "bosnia"],
    "Ivory Coast": ["ivory coast", "côte d'ivoire", "cote d'ivoire"],
    "DR Congo": ["dr congo", "congo dr", "democratic republic of congo"],
    "South Korea": ["south korea", "korea republic"],
    "Czechia": ["czechia", "czech republic"],
    "Saudi Arabia": ["saudi arabia"],
    "Cape Verde": ["cape verde"],
    "South Africa": ["south africa"],
    "New Zealand": ["new zealand"],
}


def _sofascore_names_match(our_name: str, sf_name: str) -> bool:
    sf = sf_name.lower().strip()
    our = our_name.lower().strip()
    if our == sf:
        return True
    for alias in _SOFASCORE_ALIASES.get(our_name, []):
        if alias == sf:
            return True
    return our in sf or sf in our


def _parse_sofascore_team(team_data: dict) -> "TeamLineup | None":
    formation = team_data.get("formation", "")
    players_raw = team_data.get("players", [])
    if not formation or not players_raw:
        return None
    pos_map = {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}
    starters = [
        Player(
            name=p.get("player", {}).get("name", ""),
            position=pos_map.get(p.get("position", ""), p.get("position", "")),
        )
        for p in players_raw
        if p.get("player", {}).get("name") and p.get("position")
    ]
    if len(starters) < 11:
        return None
    return TeamLineup(formation=formation, starters=starters[:11])


async def _fetch_sofascore_lineup(home_name: str, away_name: str, fixture_date: str) -> "MatchLineup | None":
    """Fetch confirmed lineup from SofaScore. Returns None if not yet confirmed."""
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=_SOFASCORE_HEADERS) as client:
            r = await client.get(
                f"{_SOFASCORE_BASE}/sport/football/scheduled-events/{fixture_date}"
            )
            r.raise_for_status()
            events = r.json().get("events", [])

            event_id = None
            for event in events:
                h = event.get("homeTeam", {}).get("name", "")
                a = event.get("awayTeam", {}).get("name", "")
                if _sofascore_names_match(home_name, h) and _sofascore_names_match(away_name, a):
                    event_id = event["id"]
                    break

            if not event_id:
                return None

            r2 = await client.get(f"{_SOFASCORE_BASE}/event/{event_id}/lineups")
            r2.raise_for_status()
            data = r2.json()

            if not data.get("confirmed"):
                return None

            home_lineup = _parse_sofascore_team(data.get("home", {}))
            away_lineup = _parse_sofascore_team(data.get("away", {}))
            if not home_lineup or not away_lineup:
                return None

            return MatchLineup(home=home_lineup, away=away_lineup, is_predicted=False)
    except Exception:
        return None


async def _fetch_team_form_espn(team_name: str) -> list[FormResult] | None:
    """Fetch last 5 completed results for a national team via ESPN (no API key needed)."""
    team_id = _ESPN_TEAM_IDS.get(team_name)
    if not team_id:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{_ESPN_BASE}/{team_id}/schedule", params={"limit": 20})
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    results: list[FormResult] = []
    for event in data.get("events", []):
        comp = event.get("competitions", [{}])[0]
        if not comp.get("status", {}).get("type", {}).get("completed", False):
            continue
        competitors = comp.get("competitors", [])
        if len(competitors) != 2:
            continue
        our = next((c for c in competitors if str(c["team"]["id"]) == str(team_id)), None)
        opp = next((c for c in competitors if str(c["team"]["id"]) != str(team_id)), None)
        if not our or not opp:
            continue
        our_score = int(our.get("score", {}).get("value", 0) or 0)
        opp_score = int(opp.get("score", {}).get("value", 0) or 0)
        winner = our.get("winner", False)
        is_draw = not winner and not opp.get("winner", False)
        result = "W" if winner else ("D" if is_draw else "L")
        opp_display = opp["team"]["displayName"]
        opp_name = _ESPN_NAME_MAP.get(opp_display, opp_display)
        opp_flag, _ = _TEAM_META.get(opp_name, ("🏳️", 80))
        home_away: str = "H" if our.get("homeAway") == "home" else "A"
        tournament = event.get("league", {}).get("name", "") or event.get("seasonType", {}).get("name", "")
        results.append(FormResult(
            result=result,  # type: ignore[arg-type]
            score_home=our_score,
            score_away=opp_score,
            opponent=opp_name,
            opponent_flag=opp_flag,
            date=event["date"][:10],
            home_or_away=home_away,  # type: ignore[arg-type]
            tournament=tournament,
        ))
        if len(results) == 5:
            break
    return results or None


_H2H_TTL = 30 * 24 * 3600  # H2H history never changes — cache 30 days

# ── International results dataset (martj42/international_results on GitHub) ───
_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
_RESULTS_CACHE: list[dict] | None = None

# Our team names → CSV dataset names
_CSV_NAME_MAP: dict[str, str] = {
    "USA": "United States",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Czechia": "Czech Republic",
    "Curacao": "Curaçao",
}


async def _load_results_csv() -> list[dict]:
    global _RESULTS_CACHE
    if _RESULTS_CACHE is not None:
        return _RESULTS_CACHE
    import csv, io
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(_RESULTS_URL)
        r.raise_for_status()
        reader = csv.DictReader(io.StringIO(r.text))
        _RESULTS_CACHE = [row for row in reader]
    return _RESULTS_CACHE


async def _fetch_h2h_csv(home_name: str, away_name: str) -> list[H2HResult] | None:
    """Get last 5 H2H results from the international results dataset."""
    csv_home = _CSV_NAME_MAP.get(home_name, home_name)
    csv_away = _CSV_NAME_MAP.get(away_name, away_name)
    try:
        rows = await _load_results_csv()
    except Exception:
        return None
    matches = [
        r for r in rows
        if r.get("home_score") and r.get("away_score")
        and r["home_score"] != "NA" and r["away_score"] != "NA"
        and {r["home_team"], r["away_team"]} == {csv_home, csv_away}
    ]
    if not matches:
        return []  # confirmed no history — don't fall through to mock
    results = []
    for r in reversed(matches[-5:]):
        home_flag, _ = _TEAM_META.get(home_name, ("🏳️", 80)) if r["home_team"] == csv_home else _TEAM_META.get(away_name, ("🏳️", 80))
        away_flag, _ = _TEAM_META.get(away_name, ("🏳️", 80)) if r["away_team"] == csv_away else _TEAM_META.get(home_name, ("🏳️", 80))
        disp_home = home_name if r["home_team"] == csv_home else away_name
        disp_away = away_name if r["away_team"] == csv_away else home_name
        results.append(H2HResult(
            date=r["date"],
            home_team=disp_home, home_flag=home_flag,
            away_team=disp_away, away_flag=away_flag,
            home_score=int(r["home_score"]),
            away_score=int(r["away_score"]),
            tournament=r.get("tournament", ""),
        ))
    return results or None


def _fixture_il_date(f: dict) -> date:
    """Return the Israel-time date for a fixture (accounts for late ET games crossing midnight IL)."""
    raw = date.fromisoformat(f["date"])
    _, day_offset = _et_to_israel(f.get("time", "00:00 ET"))
    return raw + timedelta(days=day_offset)


def _form_ttl(team_name: str) -> int:
    """Seconds until the team's next WC fixture (Israel date), so form cache refreshes after each game."""
    today = date.today()
    future_dates = [
        _fixture_il_date(f)
        for f in _WC26_FIXTURES
        if (f["home"] == team_name or f["away"] == team_name)
        and _fixture_il_date(f) > today
    ]
    if future_dates:
        next_match = min(future_dates)
        return max(3600, int((next_match - today).total_seconds()))
    return 7 * 24 * 3600


def _wc26_opponent_pool() -> list[Team]:
    """All 48 WC 2026 teams derived from the embedded fixture list."""
    seen: set[str] = set()
    teams: list[Team] = []
    for f in _WC26_FIXTURES:
        for side in ("home", "away"):
            name = f[side]
            if name not in seen:
                seen.add(name)
                teams.append(_team_from_wc26(name, len(teams) + 1))
    return teams


_WC26_OPPONENT_POOL: list[Team] = []  # populated lazily below


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
    matches = [_map_wc26_fixture_to_match(f) for f in _WC26_FIXTURES]
    return sorted(matches, key=lambda m: (m.kickoff_date, m.kickoff_time))


def _et_to_israel(time_str: str) -> tuple[str, int]:
    """Convert 'HH:MM ET' to Israel time (IDT=UTC+3, EDT=UTC-4, diff=+7h).
    Returns (time_str, day_offset) where day_offset=1 if crossing midnight."""
    try:
        h, m = map(int, time_str.strip().split()[0].split(":"))
        il_h = h + 7
        day_offset = 1 if il_h >= 24 else 0
        return f"{il_h % 24:02d}:{m:02d}", day_offset
    except Exception:
        return time_str, 0


def _map_wc26_fixture_to_match(f: dict) -> Match:
    home_team = _team_from_wc26(f["home"], f["id"] * 100)
    away_team = _team_from_wc26(f["away"], f["id"] * 100 + 1)
    h, d, a = _gen_odds(home_team.fifa_rank, away_team.fifa_rank)
    il_time, day_offset = _et_to_israel(f.get("time", "TBD"))
    kickoff_date = f.get("date", "TBD")
    if day_offset and kickoff_date != "TBD":
        kickoff_date = (date.fromisoformat(kickoff_date) + timedelta(days=1)).isoformat()
    return Match(
        id=f["id"], home_team=home_team, away_team=away_team,
        kickoff_time=il_time,
        kickoff_date=kickoff_date,
        group=f.get("group", "World Cup 2026"),
        home_odds=h, draw_odds=d, away_odds=a,
    )


def _mock_form(team: Team) -> list[FormResult]:
    global _WC26_OPPONENT_POOL
    if not _WC26_OPPONENT_POOL:
        _WC26_OPPONENT_POOL = _wc26_opponent_pool()
    rng = random.Random(team.id * 42)
    base = date(2026, 6, 1)
    results = []
    pool = [t for t in _WC26_OPPONENT_POOL if t.name != team.name]
    for i in range(5):
        opp = rng.choice(pool)
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


# API-Football team name aliases (their names → our names)
_AF_NAME_MAP: dict[str, str] = {
    "United States": "USA",
    "Côte d'Ivoire": "Ivory Coast",
    "Korea Republic": "South Korea",
    "Bosnia": "Bosnia & Herzegovina",
    "Congo DR": "DR Congo",
    "Türkiye": "Turkey",
    "New Zealand": "New Zealand",
    "IR Iran": "Iran",
}

_af_fixture_map: dict[tuple[str, str], int] = {}
_af_fixture_map_expires: float = 0.0


async def _load_af_fixture_map() -> None:
    global _af_fixture_map, _af_fixture_map_expires
    if time.time() < _af_fixture_map_expires:
        return
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_API_BASE}/fixtures",
            headers=_api_headers(),
            params={"league": _WORLD_CUP_LEAGUE_ID, "season": _WORLD_CUP_SEASON},
        )
        r.raise_for_status()
        for fix in r.json().get("response", []):
            fid = fix["fixture"]["id"]
            home = _AF_NAME_MAP.get(fix["teams"]["home"]["name"], fix["teams"]["home"]["name"])
            away = _AF_NAME_MAP.get(fix["teams"]["away"]["name"], fix["teams"]["away"]["name"])
            _af_fixture_map[(home, away)] = fid
    _af_fixture_map_expires = time.time() + 86400


_THE_ODDS_API_H2H_URL = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"

_THE_ODDS_API_NAME_MAP: dict[str, str] = {
    "Czech Republic": "Czechia",
    "United States": "USA",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
}

_PREFERRED_BOOKMAKERS = {
    "Bet365", "William Hill", "Unibet", "Paddy Power", "Bwin",
    "Betfair", "1xBet", "Betway", "Pinnacle", "Coral", "Sky Bet",
}

_the_odds_h2h_cache: list[dict] = []
_the_odds_h2h_expires: float = 0.0


async def _load_the_odds_h2h() -> None:
    global _the_odds_h2h_cache, _the_odds_h2h_expires
    if not settings.odds_api_key or time.time() < _the_odds_h2h_expires:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _THE_ODDS_API_H2H_URL,
                params={
                    "apiKey": settings.odds_api_key,
                    "regions": "eu,uk",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                },
            )
            r.raise_for_status()
            _the_odds_h2h_cache = r.json()
            _the_odds_h2h_expires = time.time() + 1800  # 30-min cache
    except Exception:
        pass


async def _fetch_the_odds_api_h2h(home_name: str, away_name: str) -> list[BookmakerOdds] | None:
    if not settings.odds_api_key:
        return None
    await _load_the_odds_h2h()
    if not _the_odds_h2h_cache:
        return None

    def normalise(n: str) -> str:
        return _THE_ODDS_API_NAME_MAP.get(n, n).lower()

    home_norm = normalise(home_name)
    away_norm = normalise(away_name)

    event = next(
        (
            e for e in _the_odds_h2h_cache
            if normalise(e["home_team"]) == home_norm and normalise(e["away_team"]) == away_norm
        ),
        None,
    )
    if not event:
        return None

    results: list[BookmakerOdds] = []
    seen: set[str] = set()
    # Preferred bookmakers first, then fill up to 8
    bookmakers = sorted(
        event.get("bookmakers", []),
        key=lambda b: (0 if b["title"] in _PREFERRED_BOOKMAKERS else 1, b["title"]),
    )
    for bm in bookmakers:
        if len(results) >= 8:
            break
        title = bm["title"]
        if title in seen:
            continue
        seen.add(title)
        market = next((m for m in bm.get("markets", []) if m["key"] == "h2h"), None)
        if not market:
            continue
        outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
        home_price = outcomes.get(event["home_team"], 0.0)
        away_price = outcomes.get(event["away_team"], 0.0)
        draw_price = outcomes.get("Draw", 0.0)
        if home_price and away_price and draw_price:
            results.append(BookmakerOdds(bookmaker=title, home=home_price, draw=draw_price, away=away_price))

    return results or None


async def _fetch_odds_api_football(
    home_name: str, away_name: str
) -> tuple[list[BookmakerOdds], list[ScoreOdd]] | None:
    if not settings.football_api_key:
        return None
    try:
        await _load_af_fixture_map()
        fixture_id = _af_fixture_map.get((home_name, away_name))
        if not fixture_id:
            return None
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{_API_BASE}/odds",
                headers=_api_headers(),
                params={"fixture": fixture_id},
            )
            r.raise_for_status()
            data = r.json().get("response", [])
        match_winner: list[BookmakerOdds] = []
        correct_score: list[ScoreOdd] = []
        for entry in data[:1]:
            for bm in entry.get("bookmakers", []):
                for bet in bm.get("bets", []):
                    if bet.get("name") == "Match Winner" and not match_winner:
                        vals = {v["value"]: float(v["odd"]) for v in bet["values"]}
                        h, d, a = vals.get("Home", 0.0), vals.get("Draw", 0.0), vals.get("Away", 0.0)
                        if h and d and a:
                            match_winner.append(BookmakerOdds(bookmaker=bm["name"], home=h, draw=d, away=a))
                    elif bet.get("name") == "Correct Score" and not correct_score:
                        for v in bet["values"]:
                            score = v["value"].replace(":", "-")
                            try:
                                correct_score.append(ScoreOdd(score=score, odds=float(v["odd"])))
                            except (ValueError, KeyError):
                                pass
        if not match_winner and not correct_score:
            return None
        return match_winner, sorted(correct_score, key=lambda s: s.odds)[:12]
    except Exception:
        return None


def _mock_odds_comparison(match: Match) -> list[BookmakerOdds]:
    rng = random.Random(match.id * 77)
    bookmakers = ["Bet365", "William Hill", "Unibet", "Paddy Power", "Bwin", "Betfair", "1xBet", "Betway"]
    return [
        BookmakerOdds(
            bookmaker=bm,
            home=round(match.home_odds + rng.uniform(-0.18, 0.18), 2),
            draw=round(match.draw_odds + rng.uniform(-0.12, 0.12), 2),
            away=round(match.away_odds + rng.uniform(-0.18, 0.18), 2),
        )
        for bm in bookmakers
    ]


def _mock_exact_scores(match: Match) -> list[ScoreOdd]:
    import math
    rng = random.Random(match.id * 31)
    rank_diff = match.away_team.fifa_rank - match.home_team.fifa_rank
    # Expected goals derived from rank gap, not capped win-prob odds
    lam_h = max(0.5, min(4.5, 1.3 + rank_diff * 0.028))
    lam_a = max(0.1, min(3.5, 1.0 - rank_diff * 0.012))

    def poisson(lam: float, k: int) -> float:
        return (lam ** k) * math.exp(-lam) / math.factorial(k)

    candidates = [(f"{h}-{a}", poisson(lam_h, h) * poisson(lam_a, a))
                  for h in range(6) for a in range(5)]
    candidates.sort(key=lambda x: -x[1])
    margin = 1.10
    return [
        ScoreOdd(score=s, odds=round(margin / p * rng.uniform(0.96, 1.04), 2))
        for s, p in candidates[:12]
    ]


# ── WC26 API helpers ──────────────────────────────────────────────────────────

def _wc26_headers() -> dict[str, str]:
    return {
        "X-RapidAPI-Key": settings.wc26_api_key,
        "X-RapidAPI-Host": settings.wc26_api_host,
    }


def _parse_wc26_time(time_str: str) -> str:
    """Convert '13:00 UTC-6' → '19:00 EST'."""
    try:
        parts = time_str.strip().split()
        h, m = map(int, parts[0].split(":"))
        offset = int(parts[1].replace("UTC", ""))
        utc_h = (h - offset) % 24
        est_h = (utc_h - 5) % 24
        return f"{est_h:02d}:{m:02d} EST"
    except Exception:
        return time_str


def _team_from_wc26(name: str, team_id: int) -> Team:
    flag, rank = _TEAM_META.get(name, ("🏳️", 80))
    return Team(id=team_id, name=name, flag=flag, fifa_rank=rank)


def _map_wc26_to_match(fixture: dict[str, Any]) -> Match:
    home_name = fixture["home"]
    away_name = fixture["away"]
    match_id = fixture["id"]
    home_team = _team_from_wc26(home_name, match_id * 100)
    away_team = _team_from_wc26(away_name, match_id * 100 + 1)
    h, d, a = _gen_odds(home_team.fifa_rank, away_team.fifa_rank)
    return Match(
        id=match_id,
        home_team=home_team,
        away_team=away_team,
        kickoff_time=_parse_wc26_time(fixture.get("time", "TBD")),
        kickoff_date=fixture.get("date", "TBD"),
        group=fixture.get("group") or fixture.get("round") or "World Cup 2026",
        home_odds=h, draw_odds=d, away_odds=a,
    )


async def _fetch_wc26_matches() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{_WC26_BASE}/matches", headers=_wc26_headers())
        r.raise_for_status()
        data = r.json()
        return data.get("data", [])


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

def _sort_matches(matches: list[Match]) -> list[Match]:
    return sorted(matches, key=lambda m: (m.kickoff_date, m.kickoff_time))


_ESPN_SCORES_CACHE: dict[str, tuple[float, tuple[int | None, int | None, str]]] = {}
# key: "HomeTeam|AwayTeam"  value: (expires_at, (score_home, score_away, status))

_ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
_ESPN_SUMMARY   = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary"

_ESPN_MATCH_NAME_MAP: dict[str, str] = {
    "Bosnia-Herz": "Bosnia & Herzegovina",
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "Bosnia & Herzegovina": "Bosnia & Herzegovina",
    "United States": "USA",
    "Czech Republic": "Czechia",
    "Czechia": "Czechia",
    "Türkiye": "Turkey",
    "Curaçao": "Curacao",
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Côte d'Ivoire": "Ivory Coast",
    "Congo DR": "DR Congo",
}

_ESPN_POS_MAP = {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}


async def fetch_espn_lineup(home_name: str, away_name: str, fixture_date: str) -> "MatchLineup | None":
    """Fetch confirmed starting lineup from ESPN. Returns None if not available yet."""
    from app.models.match import MatchLineup, TeamLineup, Player
    date_str = fixture_date.replace("-", "")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(_ESPN_SCOREBOARD, params={"dates": date_str})
            r.raise_for_status()
            events = r.json().get("events", [])

            def _norm(n: str) -> str:
                return _ESPN_MATCH_NAME_MAP.get(n, n)

            event_id = None
            for event in events:
                comps = event.get("competitions", [{}])
                competitors = comps[0].get("competitors", []) if comps else []
                names = {_norm(c.get("team", {}).get("displayName", "")) for c in competitors}
                if home_name in names and away_name in names:
                    event_id = event["id"]
                    break

            if not event_id:
                return None

            r2 = await client.get(_ESPN_SUMMARY, params={"event": event_id})
            r2.raise_for_status()
            rosters = r2.json().get("rosters", [])
            if len(rosters) < 2:
                return None

            def _parse_roster(roster_data: dict) -> "TeamLineup | None":
                athletes = roster_data.get("roster", [])
                starters = [a for a in athletes if a.get("starter")]
                if len(starters) < 11:
                    return None
                formation = roster_data.get("formation", "")
                players = [
                    Player(
                        name=a.get("athlete", {}).get("displayName", ""),
                        position=_ESPN_POS_MAP.get(a.get("position", {}).get("abbreviation", ""), "MID"),
                    )
                    for a in starters[:11]
                ]
                return TeamLineup(formation=formation, starters=players)

            home_roster = next((r for r in rosters if _norm(r.get("team", {}).get("displayName", "")) == home_name), None)
            away_roster = next((r for r in rosters if _norm(r.get("team", {}).get("displayName", "")) == away_name), None)

            if not home_roster:
                home_roster = rosters[0]
            if not away_roster:
                away_roster = rosters[1]

            home_lu = _parse_roster(home_roster)
            away_lu = _parse_roster(away_roster)
            if not home_lu or not away_lu:
                return None

            return MatchLineup(home=home_lu, away=away_lu, is_predicted=False)
    except Exception:
        return None


_SCORE_REDIS_TTL = 7 * 24 * 3600  # 7 days for finished scores in Redis


async def _load_scores_from_redis() -> None:
    """Pre-populate in-memory score cache from Redis on startup (instant, no ESPN call)."""
    from app.core.cache import get_cached
    data = await get_cached("espn_scores_v1") or {}
    now = time.time()
    for key, (expires, score_tuple) in data.items():
        if expires > now:
            _ESPN_SCORES_CACHE[key] = (expires, tuple(score_tuple))


async def fetch_scores_for_date(date_str: str) -> None:
    """Fetch ESPN scoreboard for a YYYYMMDD date string and populate _ESPN_SCORES_CACHE."""
    from app.core.cache import set_cached
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                _ESPN_SCOREBOARD,
                params={"dates": date_str},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            data = r.json()
        short_ttl = time.time() + 600       # 10-min for live/scheduled
        long_ttl  = time.time() + 7 * 86400  # 7-day for finished (score never changes)
        for event in data.get("events", []):
            comp = event.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue
            status_type = comp.get("status", {}).get("type", {})
            state = status_type.get("state", "pre")
            completed = status_type.get("completed", False)

            def _norm(n: str) -> str:
                return _ESPN_MATCH_NAME_MAP.get(n, n)

            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
            home_name = _norm(home["team"].get("shortDisplayName", ""))
            away_name = _norm(away["team"].get("shortDisplayName", ""))

            if completed or state == "post":
                try:
                    sh = int(float(home.get("score", 0)))
                    sa = int(float(away.get("score", 0)))
                except (ValueError, TypeError):
                    sh, sa = None, None
                status = "finished"
                expires = long_ttl
            elif state == "in":
                try:
                    sh = int(float(home.get("score", 0)))
                    sa = int(float(away.get("score", 0)))
                except (ValueError, TypeError):
                    sh, sa = None, None
                status = "live"
                expires = short_ttl
            else:
                sh, sa, status = None, None, "scheduled"
                expires = short_ttl

            key = f"{home_name}|{away_name}"
            _ESPN_SCORES_CACHE[key] = (expires, (sh, sa, status))

        # Persist finished scores to Redis so they survive restarts
        finished = {k: (exp, list(v)) for k, (exp, v) in _ESPN_SCORES_CACHE.items() if v[2] == "finished"}
        if finished:
            await set_cached("espn_scores_v1", finished, ttl=_SCORE_REDIS_TTL)
    except Exception:
        pass


_GROUP_STAGE_FIRST_DAY = date(2026, 6, 11)  # first WC 2026 match (ET date on ESPN)

# Pre-build {date_iso: [fixture, ...]} for fast per-date cache checks
_FIXTURES_BY_DATE: dict[str, list[dict]] = {}
for _f in _WC26_FIXTURES:
    _FIXTURES_BY_DATE.setdefault(_f["date"], []).append(_f)


async def refresh_scores_today() -> None:
    """Refresh scores from ESPN, then bust the upcoming_matches cache.

    For each date since the group stage started:
    - Always re-fetch today and yesterday (live / just-finished matches).
    - Skip older dates only when every match on that date is already
      in _ESPN_SCORES_CACHE as 'finished' (self-healing after partial restarts).
    Finished scores are persisted to Redis and loaded before the server
    starts accepting requests, so there is no scoreless window on restart.
    """
    from app.core.cache import delete_cached
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    dates_to_fetch: list[str] = []
    d = _GROUP_STAGE_FIRST_DAY
    while d <= today:
        dt = d.strftime("%Y%m%d")
        if d >= yesterday:
            # Always refresh recent dates — matches may be live or just finished
            dates_to_fetch.append(dt)
        else:
            # Past date: skip only if every fixture is already cached as finished
            fixtures = _FIXTURES_BY_DATE.get(d.isoformat(), [])
            all_done = all(
                _ESPN_SCORES_CACHE.get(f"{f['home']}|{f['away']}", (0, (None, None, "")))[1][2] == "finished"
                for f in fixtures
            )
            if not all_done:
                dates_to_fetch.append(dt)
        d += timedelta(days=1)

    if dates_to_fetch:
        await asyncio.gather(*[fetch_scores_for_date(dt) for dt in dates_to_fetch])
    await delete_cached("upcoming_matches")


def _get_cached_score(home_name: str, away_name: str) -> tuple[int | None, int | None, str]:
    key = f"{home_name}|{away_name}"
    entry = _ESPN_SCORES_CACHE.get(key)
    if entry and time.time() < entry[0]:
        return entry[1]
    return None, None, "scheduled"


def _merge_scores(matches: list[Match]) -> list[Match]:
    result = []
    for m in matches:
        sh, sa, status = _get_cached_score(m.home_team.name, m.away_team.name)
        if sh is not None:
            m = m.model_copy(update={"score_home": sh, "score_away": sa, "status": status})
        result.append(m)
    return result


async def get_upcoming_matches() -> list[Match]:
    # The live WC26 API omits finished matches, causing them to vanish from the explorer.
    # Embedded fixtures are the authoritative schedule; ESPN provides live scores on top.
    if not settings.football_api_key:
        return _merge_scores(_mock_upcoming_matches())
    try:
        fixtures = await _fetch_upcoming_fixtures()
        if not fixtures:
            return _merge_scores(_mock_upcoming_matches())
        return _merge_scores(_sort_matches([_map_fixture_to_match(f, idx + 1) for idx, f in enumerate(fixtures)]))
    except Exception:
        return _merge_scores(_mock_upcoming_matches())


async def get_match_detail(fixture_id: int) -> MatchDetail | None:
    matches = await get_upcoming_matches()
    match = next((m for m in matches if m.id == fixture_id), None)
    if match is None:
        return None

    if not settings.football_api_key or match.home_team.api_id == 0:
        from app.services.ai_service import get_team_form_web, get_h2h_web, get_lineup
        from app.core.cache import get_cached, set_cached

        home_name = match.home_team.name
        away_name = match.away_team.name
        h2h_key = "h2h:" + ":".join(sorted([home_name, away_name]))

        home_form_cached = await get_cached(f"form:{home_name}")
        away_form_cached = await get_cached(f"form:{away_name}")
        h2h_cached = await get_cached(h2h_key)

        if home_form_cached is None:
            result = await _fetch_team_form_espn(home_name)
            if not result:
                result = await get_team_form_web(home_name)
            home_form_cached = [r.model_dump() for r in result] if result else None
            if home_form_cached:
                await set_cached(f"form:{home_name}", home_form_cached, ttl=_form_ttl(home_name))

        if away_form_cached is None:
            result = await _fetch_team_form_espn(away_name)
            if not result:
                result = await get_team_form_web(away_name)
            away_form_cached = [r.model_dump() for r in result] if result else None
            if away_form_cached:
                await set_cached(f"form:{away_name}", away_form_cached, ttl=_form_ttl(away_name))

        if h2h_cached is None:
            result = await _fetch_h2h_csv(home_name, away_name)
            if result is None:
                result = await get_h2h_web(home_name, away_name)
            h2h_cached = [r.model_dump() for r in result] if result is not None else None
            if h2h_cached is not None:
                await set_cached(h2h_key, h2h_cached, ttl=_H2H_TTL)

        lineup_key = f"lineup_v2:{fixture_id}"
        lineup_raw = await get_cached(lineup_key)

        # If cached lineup is predicted (not confirmed), try SofaScore for real lineup
        if lineup_raw is None or lineup_raw.get("is_predicted", True):
            sofascore_lineup = await _fetch_sofascore_lineup(home_name, away_name, match.kickoff_date)
            if sofascore_lineup:
                lineup_raw = sofascore_lineup.model_dump()
                await set_cached(lineup_key, lineup_raw, ttl=7200)  # 2h — re-check closer to kickoff
            elif lineup_raw is None:
                lineup_obj = await get_lineup(home_name, away_name)
                if lineup_obj:
                    lineup_raw = lineup_obj.model_dump()
                    await set_cached(lineup_key, lineup_raw, ttl=_form_ttl(home_name))

        home_form = [FormResult(**r) for r in home_form_cached] if home_form_cached else _mock_form(match.home_team)
        away_form = [FormResult(**r) for r in away_form_cached] if away_form_cached else _mock_form(match.away_team)
        h2h = [H2HResult(**r) for r in h2h_cached] if h2h_cached is not None else _mock_h2h(match.home_team, match.away_team)
        real_odds = await _fetch_the_odds_api_h2h(home_name, away_name)
        odds_result = await _fetch_odds_api_football(home_name, away_name)
        odds = real_odds or (odds_result[0] if odds_result else _mock_odds_comparison(match))
        exact_scores = odds_result[1] if odds_result else _mock_exact_scores(match)

        lineup = None
        if lineup_raw:
            try:
                lineup = MatchLineup(
                    home=TeamLineup(
                        formation=lineup_raw["home"]["formation"],
                        starters=[Player(**p) for p in lineup_raw["home"]["starters"]],
                    ),
                    away=TeamLineup(
                        formation=lineup_raw["away"]["formation"],
                        starters=[Player(**p) for p in lineup_raw["away"]["starters"]],
                    ),
                    is_predicted=lineup_raw.get("is_predicted", True),
                )
            except Exception:
                lineup = None

        return MatchDetail(
            match=match,
            home_form=home_form,
            away_form=away_form,
            h2h=h2h,
            odds_comparison=odds,
            exact_scores=exact_scores,
            lineup=lineup,
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
        real_odds = await _fetch_the_odds_api_h2h(match.home_team.name, match.away_team.name)
        odds_result = await _fetch_odds_api_football(match.home_team.name, match.away_team.name)
        odds = real_odds or (odds_result[0] if odds_result else _mock_odds_comparison(match))
        exact_scores = odds_result[1] if odds_result else _mock_exact_scores(match)
        return MatchDetail(
            match=match,
            home_form=home_form or _mock_form(match.home_team),
            away_form=away_form or _mock_form(match.away_team),
            h2h=h2h or _mock_h2h(match.home_team, match.away_team),
            odds_comparison=odds,
            exact_scores=exact_scores,
        )
    except Exception:
        return MatchDetail(
            match=match,
            home_form=_mock_form(match.home_team),
            away_form=_mock_form(match.away_team),
            h2h=_mock_h2h(match.home_team, match.away_team),
            odds_comparison=_mock_odds_comparison(match),
            exact_scores=_mock_exact_scores(match),
        )
