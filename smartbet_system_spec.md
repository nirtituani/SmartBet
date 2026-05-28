# SmartBet: System Specification & AI Code-Gen Blueprint

This document contains the complete system architecture, data models, caching strategies, and UI layouts for **SmartBet**—a premium AI-powered football betting intelligence dashboard. 

---

## 1. Project Overview & Tech Stack

SmartBet is a high-performance web application designed to help users make informed football betting decisions. It aggregates match schedules, historical data, recent form, and live bookmaker odds, then feeds this context to **Anthropic's Claude 3.5 Sonnet** to generate structured, professional-grade betting predictions and value bet recommendations.

### Tech Stack
* **Backend**: FastAPI (Python 3.11+)
  * Async endpoints for performance.
  * `pydantic` for strict data validation.
  * `pydantic-settings` for secure `.env` configuration.
  * `httpx` for async external API fetching.
  * `redis` for advanced caching (reducing API costs and enabling sub-second load times).
  * `anthropic` SDK for AI prediction generation.
* **Frontend**: Next.js (React)
  * Dark-mode-first dashboard with sleek glassmorphism, harmonious color palettes, and neon glows.
  * Vanilla CSS for high-quality, customized micro-animations, layout styling, and precise visual aesthetics.
  * Responsive grids tailored for desktop and mobile viewports.

---

## 2. Data & Caching Strategy (Static vs. Dynamic)

To minimize external API costs, respect rate limits, and maintain high performance, the system divides football data into two caching tiers:

### A. Static / Semi-Static Tier (High TTL / Local DB)
* **Leagues, Teams Metadata, and Match Schedules**: Fetched once and cached for **30 days** or updated weekly.
* **Historical Results & Head-to-Head (H2H)**: Results of matches that have finished. Cached **permanently** once recorded.
* **League Standings / Tables**: Updated **once a day** after matchdays.

### B. Dynamic / Live Tier (Low TTL / Real-Time)
* **Match Lineups**: Available ~60 minutes before kickoff. Real-time fetch (cached for only 1 minute until game start).
* **Injuries & Suspensions**: Pre-match availability news. Cached for **2–4 hours**.
* **Betting Odds**: Bookmaker odds (1X2, Over/Under, BTTS). Cached for **10 minutes** to avoid stale data while protecting API limits.
* **Live In-Play Stats**: During active games (possession, shots, goals). Cached for **1 minute** or streamed.

---

## 3. UI/UX Pages & Symmetrical Layout Blueprint

The frontend implements a dark glassmorphic theme (rich slate-dark backgrounds, translucent cards, subtle gradients, and custom neon-glow backdrops).

### Page 1: Match Explorer (`/match-explorer`)
* **Header**: Brand logo `SmartBet`, navigation bar (`DASHBOARD`, `MATCH EXPLORER` (active), `LIVE ODDS`, `STATS`, `PROFIL`), search icon, notification bell, user profile avatar.
* **Title Section**: "Match Explorer" with the subtitle "FIFA World Cup 2026".
* **Daily Sections**: Organized chronologically (e.g., "Today, July 14, 2026", "Tomorrow, July 15, 2026").
* **Match Cards**:
  * Glowing neon-blue border.
  * Left side: Home team flag icon, name, and location/stadium detail.
  * Right side: Away team flag icon, name.
  * Center-bottom: Kickoff time (e.g. `20:00 EST`) and Group name.
  * Far right-bottom: Micro 1X2 odds summary (e.g., `1.75 | 3.50 | 2.10`).

### Page 2: Match Intelligence & AI Predictor (`/match/{id}`)
A balanced, highly informative 5-card layout:
* **Header**: Back-navigation button (`<- Explorer`) and page title `"Match Intelligence & AI Score Predictor"`.
* **Symmetrical Match Head**: Left: Home flag with green/blue neon glow and subtitle `FIFA RANK #1 (Brazil)`. Center: `VS` indicator. Right: Away flag with blue/red neon glow and subtitle `FIFA RANK #2 (France)`.
* **Top Row (Three Equal Columns)**:
  1. **Home Team Form (Far Left)**: Vertically lists the home team's last 5 matches with opponents, dates, scores, and W/D/L colored badges (e.g. `[W] Brazil 3 - 0 Bolivia`).
  2. **Head-to-Head (H2H) History (Middle)**: Lists the last 4-5 direct matches between the two teams, showing dates, scores, and home/away flags.
  3. **Away Team Form (Far Right)**: Vertically lists the away team's last 5 matches with opponents, dates, scores, and W/D/L colored badges (e.g. `[L] France 1 - 2 Italy`).
* **Bottom Row (Two Equal Columns)**:
  1. **Real-Time Odds Table (Left Column)**: 
     * Compares 1X2 odds across major bookmakers (Bet365, William Hill, Unibet, Paddy Power).
     * Highlighting logic: Programmatically highlights the **highest odd** in each column in green to show the user where they get the best value.
  2. **AI SmartBet Prediction (Right Column)**:
     * Enclosed in an elite golden neon glowing border.
     * Score projection (e.g., `2 - 1 (Brazil Win)`).
     * **Confidence Score**: Sleek visual progress bar representing the model's confidence (e.g., `78% Confidence`).
     * **AI Tactical Summary**: Breakdown of key drivers (recent form, H2H dominance, injuries, motivational factor).
     * **Value Bet Recommendation**: Highlighted badge showing the best mathematical bet (e.g., `Value Bet: Both Teams to Score (BTTS) @ 1.85`).

---

## 4. Anthropic AI Integration Specification

The backend compiles an enriched prompt containing:
1. Team rankings, season standings, and goal differentials.
2. Symmetrical historical form (last 5 matches with opponents/scores for each).
3. H2H statistics.
4. Pre-match context: Lineups, injuries, and suspensions.
5. Current bookmaker odds.

The AI is prompted to return a strictly structured JSON response.

### Target Output JSON Schema
```json
{
  "projected_score": {
    "home_goals": 2,
    "away_goals": 1,
    "outcome_summary": "Brazil Win"
  },
  "confidence_percentage": 78,
  "tactical_analysis": "High confidence prediction based on current home advantage, superior attack rating, and recent H2H results. Probability distribution shows slight edge for Brazil in a competitive match.",
  "key_factors": [
    "Brazil has won 4 of their last 5 home games.",
    "France is missing their starting center-back due to injury.",
    "Historical H2H shows a strong tendency for home side wins."
  ],
  "value_bet": {
    "recommendation": "Both Teams to Score (BTTS)",
    "target_odds": 1.85,
    "rational": "Both teams feature elite attacking squads, and France has conceded in 4 consecutive away fixtures."
  }
}
```

---

## 5. Master Prompt for Code Generation

*Copy and paste the prompt below into another AI to build the complete SmartBet application.*

***

```markdown
You are an expert full-stack software architect specializing in FastAPI (Python) and Next.js (React).
You will build the **SmartBet** web application in its entirety, conforming strictly to the system architecture and UI blueprint specified below.

### 📋 Setup & Architecture Requirements

1. **Backend (FastAPI)**:
   - Create a layered directory structure:
     `backend/requirements.txt`
     `backend/app/main.py`
     `backend/app/core/config.py`
     `backend/app/services/football_api.py` (API clients and Redis caching)
     `backend/app/services/ai_service.py` (Anthropic Client)
     `backend/app/api/v1/endpoints/matches.py` (API Router)
   - **Caching Implementation**: Integrate Redis. Use long-term cache (30-day TTL) for leagues, teams, and fixture schedules. Use short-term cache (10-minute TTL) for dynamic betting odds, lineups, and injury lists. If Redis is unavailable, gracefully fall back to a thread-safe in-memory cache.
   - **AI Client**: Connect to Anthropic's Claude 3.5 Sonnet using the official SDK. Program the service to assemble match facts (standings, H2H, dynamic lineups, odds) and enforce a structured JSON response corresponding exactly to the blueprint's schema.

2. **Frontend (Next.js & Vanilla CSS)**:
   - Setup a modern Next.js project. Create paths for `/match-explorer` and `/match/[id]`.
   - **Theme & Styling**: Apply a dark glassmorphism design language using custom vanilla CSS. Design transparent card overlays with `backdrop-filter: blur(12px)`, custom dark slate gradients, and rich neon glows. 
   - **Highlights**: Color-code all match states. Program the odds table to dynamically locate and highlight the best available odds across bookmakers in green. Encase the AI prediction card in an elite, glowing golden neon border.

### 🛠️ Step-by-Step Implementation Instructions

1. **Step 1: Backend Setup & Models**
   - Define Pydantic response and request models for Matches, H2H history, Standings, Lineups, Odds, and AI Predictions.
   - Create the configuration module using `pydantic-settings` to load environments like `FOOTBALL_API_KEY`, `ANTHROPIC_API_KEY`, and `REDIS_URL`.

2. **Step 2: API & Mock Client Integration**
   - In `football_api.py`, write mock services that generate highly realistic, statistically sound test data representing leagues, matches, and head-to-head records so the app works out of the box. Make sure the odds are realistic (e.g., ~2.10 for Home, ~3.40 for Draw, ~3.10 for Away) rather than mathematically impossible values.
   - Implement the Redis/in-memory caching decorators to route data fetches.

3. **Step 3: Anthropic AI Predictor Service**
   - Write the prompt assembly logic in `ai_service.py`. Send the compiled facts to Anthropic's SDK.
   - Parse the response into the structured JSON prediction schema. If the LLM response fails validation, execute a robust fallback routine that returns structured mock projections.

4. **Step 4: FastAPI Router & Server**
   - Wire up the routes `/api/v1/matches/upcoming` and `/api/v1/matches/{fixture_id}/predictions`. Include full logging and robust error-handling middleware.

5. **Step 5: Next.js Pages & Styling**
   - Build the `Match Explorer` page displaying upcoming matches categorized by date, styled exactly like the provided reference.
   - Build the `Match Intelligence & AI Score Predictor` details page with:
     - The glowing, ranked team header.
     - The top row: Home Form (left) | H2H (center) | Away Form (right).
     - The bottom row: Dynamic Odds Comparison Table (left) | Golden-neon AI Prediction Widget with Confidence Meter and Value Bet badges (right).
     - Add micro-animations (subtle hover lifts, glowing border pulses) to make the experience feel exceptionally premium.

Build this codebase cleanly, writing robust, production-grade code for every file. Do not use placeholders or omit logic. Ensure all features compile and run flawlessly.
```
