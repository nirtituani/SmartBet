# SmartBet

AI-powered FIFA World Cup 2026 betting intelligence app. Aggregates match data, team form, head-to-head history, bookmaker odds, and real lineups — then uses Claude AI to produce score predictions and value bet recommendations.

## Live Features

| Page | Description |
|---|---|
| **Match Explorer** | All upcoming WC 2026 fixtures grouped by date |
| **Groups** | Live group standings (A–L) |
| **Bracket** | Full tournament bracket |
| **Match Intelligence** | Per-match deep-dive: form, H2H, odds, lineup, AI prediction |
| **WC Odds** | Winner odds — Bookmakers tab (real bookie odds) + Prediction Market tab (Polymarket) |

### Match Intelligence details
- Team form (last 5 results)
- Head-to-head history
- Live odds comparison across bookmakers
- Real lineups from SofaScore (falls back to AI-predicted lineup before kickoff)
- AI score prediction with confidence bar, tactical analysis, key factors, and value bet
- Timestamp showing when the AI prediction was last computed
- Exact score odds grid

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, CSS Modules |
| Backend | FastAPI (Python), Pydantic v2 |
| AI | Anthropic Claude (claude-sonnet-4-5) |
| Cache | Redis (Railway) |
| Lineups | SofaScore unofficial API |
| Bookmaker odds | The Odds API |
| Tournament winner odds | Polymarket Gamma API (free) |
| Hosting | Railway (backend + Redis), Railway/Vercel (frontend) |

## Environment Variables

### Backend (Railway)
| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key for AI predictions |
| `REDIS_URL` | Redis connection URL (internal: `redis.railway.internal:6379`) |
| `ODDS_API_KEY` | The Odds API key for bookmaker WC winner odds |

### Frontend (Railway/Vercel)
| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend URL (e.g. `https://your-backend.railway.app`) |

## Architecture

```
frontend (Next.js)
  └── /api/v1/*  →  backend (FastAPI)
                        ├── Redis cache (match details, odds, standings)
                        ├── Anthropic Claude  (AI predictions)
                        ├── SofaScore API     (real lineups)
                        ├── The Odds API      (bookmaker WC winner odds)
                        └── Polymarket API    (prediction market odds)
```

### Cache Warmup
On startup the backend runs a background warmup that pre-computes AI predictions for all upcoming matches:
- **Full warmup**: processes all uncached matches on startup (sorted by kickoff date, earliest first)
- **Daily refresh**: every 24 hours, force-refreshes the next 5 upcoming matches
- **Budget cap**: `$1.00/day` (20 matches × $0.05 each) — prevents runaway AI spend
- Matches already cached with a valid prediction and timestamp are skipped

### Lineup logic
1. Check Redis for a confirmed SofaScore lineup (cached 2 hours)
2. If no confirmed lineup, fetch from SofaScore's unofficial API
3. If SofaScore has no confirmed data yet, fall back to AI-predicted lineup

### Bilingual support
Full EN/HE toggle with RTL layout. Hebrew team names, dates, and UI strings throughout. Mobile hamburger drawer slides from left (EN) or right (HE).

## Local Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in keys
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Cost Management

| Item | Cost |
|---|---|
| AI prediction per match | ~$0.05 |
| Daily warmup cap | $1.00 (20 matches) |
| Daily refresh (next 5 matches) | ~$0.25 |
| The Odds API | Free tier (500 req/month) |
| Polymarket | Free, no key required |
| SofaScore | Free, no key required |
