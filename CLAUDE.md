# InfluenceHub — Influencer Campaign Management

CS348 semester project. Flask/SQLAlchemy/SQLite backend + Next.js/React/Tailwind frontend.

## Layout

- `backend/` — Flask API
  - `app.py` — routes + app factory (runs on `127.0.0.1:5000`)
  - `models.py` — SQLAlchemy models
  - `config.py` — `SQLALCHEMY_DATABASE_URI` (SQLite at `backend/site.db`)
  - `seed.py` — drops & recreates tables, loads sample data
  - `env/` — Python venv (gitignored)
- `frontend/web-app/` — Next.js 16 app router
  - `app/layout.tsx` — root layout with nav (`InfluenceHub`)
  - `app/page.tsx` — landing
  - `app/campaigns/page.tsx` — CRUD UI for campaigns
  - `app/report/page.tsx` — filterable report with stats

## Data model

- **Brand** — `id, name, industry, contact_email`. Has many campaigns.
- **Influencer** — `id, name, email (unique), platform, follower_count, engagement_rate`.
- **Campaign** — `id, title, description, budget, start_date, end_date, brand_id (FK), platform, status`.
- **campaign_influencers** — join table with extra columns `agreed_rate`, `status`. ON DELETE CASCADE both sides.

## API (all under `/api`)

- `GET  /brands` — list (read-only)
- `GET  /influencers` — list (read-only)
- `GET  /campaigns` — list (ordered by `start_date desc`)
- `GET  /campaigns/<id>`
- `POST /campaigns` — body includes `influencer_ids[]`
- `PUT  /campaigns/<id>` — partial update; if `influencer_ids` present, replaces assignments
- `DELETE /campaigns/<id>`
- `GET  /reports/campaigns` — query params `start_date`, `end_date`, `brand_id`, `platform`, `status`; returns `{campaigns, statistics}`

Dates are `YYYY-MM-DD` strings. Backend serializes via `campaign_to_dict` in `app.py`.

## Run

Backend (from `backend/`):
```
source env/bin/activate
python seed.py        # first time / reset DB
python app.py         # serves on http://127.0.0.1:5000
```
`app.py` calls `db.create_all()` on startup, so schema is auto-applied.

Frontend (from `frontend/web-app/`):
```
npm run dev           # http://localhost:3000
```
The API base URL is hardcoded as `const API = "http://127.0.0.1:5000/api"` in each page that fetches. Backend has `CORS(app)` enabled for all origins.

## Conventions

- Backend route handlers serialize manually (no Marshmallow). When adding fields to a model, also update `campaign_to_dict` and the inline list comprehensions in `get_brands`/`get_influencers`.
- Frontend pages are `'use client'` — they fetch on mount with `useEffect` and re-fetch after mutations via a local `fetchAll()`.
- Tailwind v4 with dark-styled forms (`bg-gray-900`, `border-gray-700`); status badges use color-coded pills.
- No tests, no linting in CI. `npm run lint` runs ESLint locally.

## Course constraints (Stage 3, due 2026-05-01)

The grading rubric expects:
- **SQL injection protection** — SQLAlchemy ORM uses parameterized queries by default; if raw SQL is added, use `text()` with bound params, never f-strings.
- **Indexes** — currently none beyond PKs/FK implicit indexes. Likely candidates: `campaigns.start_date`, `campaigns.brand_id`, `campaigns.platform`, `campaigns.status` (all used as report filters).
- **Transactions + isolation levels** — SQLite default is serializable; multi-step writes (e.g., create-campaign-with-influencers) should be wrapped explicitly.

Frontend just needs to function — evaluation is on the DB/SQL side.
