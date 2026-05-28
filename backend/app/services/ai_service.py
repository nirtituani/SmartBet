import json

import anthropic

from app.core.config import settings
from app.models.match import AIPrediction, BookmakerOdds, FormResult, H2HResult, Match, ProjectedScore, ValueBet

_SYSTEM_PROMPT = """You are an expert football analyst. Given match data, return a JSON prediction with this exact schema:
{
  "projected_score": {"home_goals": <int>, "away_goals": <int>, "outcome_summary": "<string>"},
  "confidence_percentage": <int 0-100>,
  "tactical_analysis": "<string, 2-3 sentences>",
  "key_factors": ["<string>", "<string>", "<string>"],
  "value_bet": {"recommendation": "<string>", "target_odds": <float>, "rational": "<string>"}
}
Return ONLY valid JSON, no markdown, no extra text."""


def _build_prompt(
    match: Match,
    home_form: list[FormResult],
    away_form: list[FormResult],
    h2h: list[H2HResult],
    odds: list[BookmakerOdds],
) -> str:
    home, away = match.home_team, match.away_team

    def form_line(r: FormResult, team_name: str) -> str:
        return f"  [{r.result}] {team_name} {r.score_home}-{r.score_away} {r.opponent} ({r.date})"

    home_str = "\n".join(form_line(r, home.name) for r in home_form)
    away_str = "\n".join(form_line(r, away.name) for r in away_form)
    h2h_str = "\n".join(
        f"  {r.home_team} {r.home_score}-{r.away_score} {r.away_team} ({r.date})" for r in h2h
    )
    odds_str = "\n".join(
        f"  {o.bookmaker}: 1={o.home}  X={o.draw}  2={o.away}" for o in odds
    )

    return f"""Match: {home.name} (FIFA #{home.fifa_rank}) vs {away.name} (FIFA #{away.fifa_rank})
Date: {match.kickoff_date} {match.kickoff_time}

{home.name} last 5 matches:
{home_str}

{away.name} last 5 matches:
{away_str}

Head-to-Head (last 5):
{h2h_str}

Current bookmaker odds:
{odds_str}

Provide your prediction as JSON."""


def _mock_prediction(match: Match) -> AIPrediction:
    home, away = match.home_team, match.away_team
    diff = away.fifa_rank - home.fifa_rank
    if diff > 3:
        hg, ag, outcome, conf = 2, 1, f"{home.name} Win", 72
    elif diff < -3:
        hg, ag, outcome, conf = 1, 2, f"{away.name} Win", 68
    else:
        hg, ag, outcome, conf = 1, 1, "Draw", 55

    return AIPrediction(
        projected_score=ProjectedScore(home_goals=hg, away_goals=ag, outcome_summary=outcome),
        confidence_percentage=conf,
        tactical_analysis=(
            f"Based on FIFA rankings, {home.name} (#{home.fifa_rank}) and {away.name} "
            f"(#{away.fifa_rank}) are closely matched. The home side holds a slight tactical "
            f"advantage given recent form and home support."
        ),
        key_factors=[
            f"{home.name} ranks #{home.fifa_rank} and holds home advantage.",
            f"{away.name} ranks #{away.fifa_rank} and will rely on counter-attacks.",
            "Historical H2H shows tight, competitive encounters between both sides.",
        ],
        value_bet=ValueBet(
            recommendation="Both Teams to Score (BTTS)",
            target_odds=round(match.home_odds * 0.85, 2),
            rational=(
                f"Both {home.name} and {away.name} possess elite attacking units "
                f"and have conceded in recent fixtures."
            ),
        ),
    )


async def get_prediction(
    match: Match,
    home_form: list[FormResult],
    away_form: list[FormResult],
    h2h: list[H2HResult],
    odds: list[BookmakerOdds],
) -> AIPrediction:
    if not settings.anthropic_api_key:
        return _mock_prediction(match)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {"role": "user", "content": _build_prompt(match, home_form, away_form, h2h, odds)}
            ],
        )
        data = json.loads(response.content[0].text.strip())
        return AIPrediction(
            projected_score=ProjectedScore(**data["projected_score"]),
            confidence_percentage=data["confidence_percentage"],
            tactical_analysis=data["tactical_analysis"],
            key_factors=data["key_factors"],
            value_bet=ValueBet(**data["value_bet"]),
        )
    except Exception:
        return _mock_prediction(match)
