# Implementation Plan - SmartBet

SmartBet is a high-performance web application designed to help users make informed football betting decisions. It aggregates real-time match data, team statistics, and betting odds, then leverages AI to provide actionable betting recommendations.

## User Review Required

> [!IMPORTANT]
> **External API Selection**: You mentioned `API-Football` and `Sportmonks`. I will start with `API-Football` as it is very well-documented. Do you already have an API key, or should I use mock data for now?

> [!NOTE]
> **Frontend Choice**: I recommend using **Next.js with Tailwind CSS** for the frontend to ensure a premium, responsive feel and good SEO. I will set this up in a `frontend/` directory.

## Proposed Changes

### [Backend] FastAPI Architecture
I will implement the layered architecture you provided to ensure the project is professional and scalable.

#### [NEW] [requirements.txt](file:///Users/nirtituani/Downloads/SmartBet/backend/requirements.txt)
- `fastapi`, `uvicorn`, `pydantic-settings`
- `httpx` (for async API calls)
- `openai` or `anthropic` (for AI predictions)
- `redis` (for caching)

#### [NEW] [app/main.py](file:///Users/nirtituani/Downloads/SmartBet/backend/app/main.py)
- Main FastAPI entry point with CORS settings and router inclusion.

#### [NEW] [app/core/config.py](file:///Users/nirtituani/Downloads/SmartBet/backend/app/core/config.py)
- Configuration management using `pydantic-settings` to handle `.env` variables safely.

#### [NEW] [app/services/football_api.py](file:///Users/nirtituani/Downloads/SmartBet/backend/app/services/football_api.py)
- Client to interface with the external Football API.

#### [NEW] [app/services/ai_service.py](file:///Users/nirtituani/Downloads/SmartBet/backend/app/services/ai_service.py)
- Logic for building prompts and getting structured JSON predictions from the LLM.

#### [NEW] [app/api/v1/endpoints/matches.py](file:///Users/nirtituani/Downloads/SmartBet/backend/app/api/v1/endpoints/matches.py)
- Endpoints for `upcoming` matches, `stats`, and `predictions`.

---

### [Frontend] Next.js Dashboard
A modern, vibrant UI to display the betting data and AI recommendations.

#### [NEW] [frontend/](file:///Users/nirtituani/Downloads/SmartBet/frontend/)
- Initialization of a Next.js project using Tailwind CSS and Lucide icons.

## Open Questions

1. **AI Model**: Would you prefer using **OpenAI (GPT-4o)** or **Anthropic (Claude 3.5)** for the betting predictions?
2. **Design**: Should I generate a **Pencil** design first to visualize the match detail pages and the "AI Prediction" widget?

## Verification Plan

### Automated Tests
- Terminal-based testing of the FastAPI endpoints using `curl` or `httpx`.
- Validation of Pydantic schemas against mock API data.

### Manual Verification
- Browsing the Next.js frontend to verify the match list and prediction layout.
- Checking Redis logs to ensure caching is working correctly.
