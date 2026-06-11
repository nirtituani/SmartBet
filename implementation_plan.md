# SmartBet — Implementation Record

This document tracks what has been built, the key decisions made, and the current state of the system.

---

## What's Built

### Backend (`/backend`)

#### Core
- **`app/main.py`** — FastAPI app with CORS, lifespan context manager that fires background warmup on startup
- **`app/core/config.py`** — Pydantic settings: `ANTHROPIC_API_KEY`, `REDIS_URL`, `ODDS_API_KEY`, `FOOTBALL_API_KEY`
- **`app/core/cache.py`** — Single persistent Redis connection pool (`aioredis`); `get_cached` / `set_cached` helpers; falls back to in-memory if Redis is unavailable
- **`app/core/budget.py`** — Daily AI spend tracker in Redis (`daily_spend:{YYYY-MM-DD}`). `DAILY_LIMIT_USD = $1.00`, `COST_PER_MATCH = $0.05`. Prevents runaway Anthropic spend.
- **`app/models/match.py`** — Pydantic models: `Team`, `Match`, `MatchDetail`, `AIPrediction`, `MatchLineup`, `FormResult`, `H2HResult`, `BookmakerOdds`, `ScoreOdd`, `StandingRow`

#### Services
- **`app/services/football_api.py`**
  - Embedded WC 2026 fixture schedule (no API needed for match list)
  - `_TEAM_META`: flag emoji + FIFA rank for all 48 WC teams
  - `get_upcoming_matches()` — returns all fixtures
  - `get_match_detail(fixture_id)` — builds full match context: form, H2H, odds, lineup
  - `_fetch_sofascore_lineup()` — fetches confirmed lineups from SofaScore's unofficial API; only returns if `confirmed: true`; falls back to AI if unconfirmed
  - Group standings from embedded CSV data

- **`app/services/ai_service.py`** — Calls Anthropic Claude to generate: projected score, confidence %, tactical analysis, key factors, value bet recommendation, exact score odds

- **`app/services/warmup.py`**
  - `full_warmup()` — on startup, computes all matches missing lineup OR `prediction_updated_at`; sorted by kickoff date (earliest first); respects daily budget
  - `daily_refresh()` — every 24 hours, force-refreshes the next 5 upcoming matches
  - `warm_cache()` — runs full warmup then loops daily refresh forever

#### API Endpoints
- `GET /api/v1/matches/upcoming` — list of all upcoming fixtures (cached 6h)
- `GET /api/v1/matches/{id}/predictions` — full match detail with AI prediction (served from cache; computed on-demand if not cached)
- `GET /api/v1/groups/standings` — group standings A–L
- `POST /api/v1/groups/standings/refresh` — force-refresh standings
- `GET /api/v1/odds/wc-winner` — WC winner odds from Polymarket (cached 1h)
- `GET /api/v1/odds/wc-winner-bookmakers` — best bookmaker WC winner odds from The Odds API (cached 1h)
- `GET /health` — shows Redis status, AI enabled, daily spend vs limit

---

### Frontend (`/frontend`)

Next.js 15.5 / React 19 / TypeScript. No UI framework — all custom CSS with CSS variables and glassmorphism design system.

#### Pages
| Route | File | Description |
|---|---|---|
| `/` | `app/page.tsx` | Redirects to `/match-explorer` |
| `/match-explorer` | `app/match-explorer/` | All upcoming matches grouped by date |
| `/groups` | `app/groups/` | Group standings table (A–L) |
| `/bracket` | `app/bracket/` | Tournament bracket |
| `/match/[id]` | `app/match/[id]/` | Match intelligence — form, H2H, odds, lineup, AI prediction |
| `/odds` | `app/odds/` | WC winner odds — Bookmakers tab + Prediction Market tab |

#### Components
- `Header.tsx` — sticky nav with EN/HE toggle, hamburger drawer (slides left for EN, right for HE)
- `TeamForm.tsx` — last 5 results + lineup tab (pitch visualization or list)
- `H2HHistory.tsx` — head-to-head results
- `OddsTable.tsx` — bookmaker odds comparison
- `AIPrediction.tsx` — AI score card with confidence bar and value bet
- `ExactScores.tsx` — exact score probability grid
- `PitchLineup.tsx` — SVG pitch with player positions

#### i18n
- `lib/i18n.ts` — full EN/HE translation object (`as const`), team name map, `translateTeam()` / `translateGroup()` helpers
- `contexts/LanguageContext.tsx` — persists language to `localStorage`
- RTL layout via `dir="rtl"` on root elements when `lang === 'he'`

#### Data flow pattern
Server component fetches initial data → passes as props to `'use client'` component → client re-fetches on mount for freshness.

---

## Key Decisions & Rationale

| Decision | Rationale |
|---|---|
| Embedded fixture schedule instead of live API | API-Football free tier didn't include WC 2026; SofaScore doesn't have a stable fixtures API. Embedding is reliable and free. |
| SofaScore for lineups | Free unofficial API; returns `confirmed: true` flag so we only use real data; falls back to AI when unconfirmed |
| Polymarket for winner odds | Free, no API key, real-money prediction market with deep liquidity |
| The Odds API for bookmaker odds | Aggregates real bookmaker prices (Bet365, Betfair etc); free tier 500 req/month |
| Redis persistent connection pool | Per-call connections caused "Future exception was never retrieved" errors and reconnect overhead |
| Skip warmup if cached + has timestamp | Prevents redundant AI spend on redeployment; one-time migration effect for entries from before timestamp feature |
| Daily budget cap in Redis | Prevents runaway costs; resets daily; tracked even if Redis fails (in-memory fallback) |
| `force=True` in daily refresh | Ensures the next upcoming matches always have fresh predictions, bypassing the skip-if-cached logic |

---

## Environment Variables (Railway)

### Backend service
```
ANTHROPIC_API_KEY=...
REDIS_URL=redis://...
ODDS_API_KEY=60a749c2fb47541dca31c93353d06be4
```

### Frontend service
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Pending / Known Limitations

- **Slow load on uncached matches**: With $1/day cap, only ~20 matches warm per day. Games not yet in cache trigger on-demand AI computation (~10–15s). Resolves as warmup runs daily.
- **Lineups**: SofaScore only provides confirmed lineups ~1h before kickoff. Before that, lineup is AI-predicted (`is_predicted: true`).
- **Standings**: Derived from match results in embedded CSV, not a live feed.
- **Bracket**: Static structure seeded from group standings; not auto-advancing based on results yet.
