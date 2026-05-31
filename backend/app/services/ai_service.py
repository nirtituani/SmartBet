import json
import re

import anthropic

from app.core.config import settings
from app.models.match import AIPrediction, BookmakerOdds, FormResult, H2HResult, Match, ProjectedScore, ValueBet

_FORM_PROMPT = """List {team} national football team's 5 most recent international match results. Include matches from 2022-2025 (World Cups, Nations League, qualifiers, friendlies).

Return ONLY a JSON array with exactly 5 objects, no markdown, no explanation:
[
  {{
    "result": "W",
    "score_home": 2,
    "score_away": 1,
    "opponent": "Germany",
    "opponent_flag": "🇩🇪",
    "date": "2025-03-25",
    "home_or_away": "H"
  }}
]

score_home = {team}'s goals, score_away = opponent's goals.
result = W/D/L from {team}'s perspective.
home_or_away = H if {team} was home team, A if away.
Return ONLY the JSON array, starting with [."""

_H2H_PROMPT = """List the 5 most recent head-to-head international football matches between {home} and {away}. Include any era (World Cups, friendlies, tournaments).

Return ONLY a JSON array with exactly 5 objects, no markdown, no explanation:
[
  {{
    "date": "2023-06-15",
    "home_team": "{home}",
    "home_flag": "🇧🇷",
    "away_team": "{away}",
    "away_flag": "🇫🇷",
    "home_score": 1,
    "away_score": 0
  }}
]

home_team/away_team = whichever team was actually at home that day.
Return ONLY the JSON array, starting with [."""


def _extract_json_array(text: str) -> list | None:
    match = re.search(r'\[[\s\S]*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


async def _claude_ask(prompt: str) -> str | None:
    """Ask Claude using training knowledge only (no web search, low token cost)."""
    if not settings.anthropic_api_key:
        return None
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in response.content
            if getattr(block, "type", "") == "text" and block.text
        ) or None
    except Exception:
        return None


async def get_team_form_web(team_name: str) -> list[FormResult] | None:
    """Fetch last 5 results for a team using Claude's training knowledge."""
    text = await _claude_ask(_FORM_PROMPT.format(team=team_name))
    if not text:
        return None
    data = _extract_json_array(text)
    if not data:
        return None
    try:
        return [FormResult(**r) for r in data]
    except Exception:
        return None


async def get_h2h_web(home_name: str, away_name: str) -> list[H2HResult] | None:
    """Fetch H2H history between two teams using Claude's training knowledge."""
    text = await _claude_ask(_H2H_PROMPT.format(home=home_name, away=away_name))
    if not text:
        return None
    data = _extract_json_array(text)
    if not data:
        return None
    try:
        return [H2HResult(**r) for r in data]
    except Exception:
        return None

_SYSTEM_PROMPT = """You are an expert football analyst specialising in the FIFA World Cup 2026. Given match data, return a JSON prediction using this exact schema:
{
  "projected_score": {"home_goals": <int>, "away_goals": <int>, "outcome_summary": "<string>"},
  "confidence_percentage": <int 0-100>,
  "tactical_analysis": "<string, 3-4 sentences — include tactical style, pressing, set-pieces, anything relevant>",
  "key_factors": ["<string>", "<string>", "<string>", "<string>", "<string>"],
  "additional_context": "<string — include anything else relevant: injuries, suspensions, squad depth, motivation, climate, altitude, travel fatigue, group stage standings pressure, manager history, star player form>",
  "value_bet": {"recommendation": "<string>", "target_odds": <float>, "rational": "<string>"}
}
Draw on your full knowledge of these teams — squad depth, manager style, recent injuries, key players, World Cup history, psychological factors, anything that matters.
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

    return f"""Tournament: FIFA World Cup 2026 — {match.group}
Match: {home.name} (FIFA #{home.fifa_rank}) vs {away.name} (FIFA #{away.fifa_rank})
Kickoff: {match.kickoff_date} {match.kickoff_time} (Israel time)

{home.name} last 5 matches:
{home_str}

{away.name} last 5 matches:
{away_str}

Head-to-Head (last 5):
{h2h_str}

Current bookmaker odds:
{odds_str}

Use your full knowledge of both teams (squad, injuries, manager, style, World Cup history, motivation) to provide a deep prediction as JSON."""


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
        additional_context=(
            f"Both squads arrive at the FIFA World Cup 2026 with strong motivations. "
            f"Squad depth, set-piece delivery, and late-game fitness will be decisive factors."
        ),
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
            max_tokens=2048,
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
        raw = "".join(
            block.text for block in response.content
            if getattr(block, "type", "") == "text" and block.text
        ).strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw.strip())
        data = json.loads(raw)
        return AIPrediction(
            projected_score=ProjectedScore(**data["projected_score"]),
            confidence_percentage=data["confidence_percentage"],
            tactical_analysis=data["tactical_analysis"],
            key_factors=data["key_factors"],
            additional_context=data.get("additional_context", ""),
            value_bet=ValueBet(**data["value_bet"]),
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"[AI] prediction failed: {e}")
        return _mock_prediction(match)


_LINEUP_PROMPT = """Predict the most likely starting XI and formation for both teams in this FIFA World Cup 2026 match. Use your full knowledge of each squad's typical manager formation and first-choice players as of 2025/2026.

Match: {home} vs {away}
Tournament: FIFA World Cup 2026

Return ONLY valid JSON, no markdown:
{{
  "home": {{
    "formation": "4-3-3",
    "starters": [
      {{"name": "Player Name", "position": "GK"}},
      {{"name": "Player Name", "position": "RB"}},
      {{"name": "Player Name", "position": "CB"}},
      {{"name": "Player Name", "position": "CB"}},
      {{"name": "Player Name", "position": "LB"}},
      {{"name": "Player Name", "position": "CM"}},
      {{"name": "Player Name", "position": "CM"}},
      {{"name": "Player Name", "position": "CM"}},
      {{"name": "Player Name", "position": "RW"}},
      {{"name": "Player Name", "position": "ST"}},
      {{"name": "Player Name", "position": "LW"}}
    ]
  }},
  "away": {{
    "formation": "4-2-3-1",
    "starters": [
      {{"name": "Player Name", "position": "GK"}},
      {{"name": "Player Name", "position": "RB"}},
      {{"name": "Player Name", "position": "CB"}},
      {{"name": "Player Name", "position": "CB"}},
      {{"name": "Player Name", "position": "LB"}},
      {{"name": "Player Name", "position": "CDM"}},
      {{"name": "Player Name", "position": "CDM"}},
      {{"name": "Player Name", "position": "CAM"}},
      {{"name": "Player Name", "position": "RW"}},
      {{"name": "Player Name", "position": "LW"}},
      {{"name": "Player Name", "position": "ST"}}
    ]
  }}
}}"""


async def get_lineup(home_name: str, away_name: str) -> "MatchLineup | None":
    from app.models.match import MatchLineup, TeamLineup, Player
    if not settings.anthropic_api_key:
        return None
    text = await _claude_ask(_LINEUP_PROMPT.format(home=home_name, away=away_name))
    if not text:
        return None
    try:
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text.strip())
        data = json.loads(text)
        return MatchLineup(
            home=TeamLineup(
                formation=data["home"]["formation"],
                starters=[Player(**p) for p in data["home"]["starters"]],
            ),
            away=TeamLineup(
                formation=data["away"]["formation"],
                starters=[Player(**p) for p in data["away"]["starters"]],
            ),
        )
    except Exception:
        return None
