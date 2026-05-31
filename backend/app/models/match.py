from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class Team(BaseModel):
    id: int
    name: str
    flag: str
    fifa_rank: int
    api_id: int = 0    # API-Football team ID (0 = mock/unknown)


class FormResult(BaseModel):
    opponent: str
    opponent_flag: str
    date: str
    score_home: int
    score_away: int
    result: Literal["W", "D", "L"]
    home_or_away: Literal["H", "A"]
    tournament: str = ""


class H2HResult(BaseModel):
    date: str
    home_team: str
    home_flag: str
    away_team: str
    away_flag: str
    home_score: int
    away_score: int
    tournament: str = ""


class StandingRow(BaseModel):
    name: str
    flag: str
    fifa_rank: int
    mp: int
    w: int
    d: int
    l: int
    gf: int
    ga: int
    gd: int
    pts: int


class BookmakerOdds(BaseModel):
    bookmaker: str
    home: float
    draw: float
    away: float


class Match(BaseModel):
    id: int
    home_team: Team
    away_team: Team
    kickoff_time: str
    kickoff_date: str
    group: str
    home_odds: float
    draw_odds: float
    away_odds: float


class ProjectedScore(BaseModel):
    home_goals: int
    away_goals: int
    outcome_summary: str


class ValueBet(BaseModel):
    recommendation: str
    target_odds: float
    rational: str


class AIPrediction(BaseModel):
    projected_score: ProjectedScore
    confidence_percentage: int
    tactical_analysis: str
    key_factors: list[str]
    additional_context: str = ""
    value_bet: ValueBet


class ScoreOdd(BaseModel):
    score: str
    odds: float


class Player(BaseModel):
    name: str
    position: str  # e.g. "GK", "CB", "LB", "RB", "CM", "CAM", "LW", "RW", "ST"


class TeamLineup(BaseModel):
    formation: str  # e.g. "4-3-3"
    starters: list[Player]


class MatchLineup(BaseModel):
    home: TeamLineup
    away: TeamLineup
    is_predicted: bool = True


class MatchDetail(BaseModel):
    match: Match
    home_form: list[FormResult]
    away_form: list[FormResult]
    h2h: list[H2HResult]
    odds_comparison: list[BookmakerOdds]
    exact_scores: list[ScoreOdd] = []
    prediction: AIPrediction | None = None
    lineup: MatchLineup | None = None
