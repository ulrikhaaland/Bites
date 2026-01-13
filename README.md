# Bites

Local-first MyFitnessPal analytics with a FastAPI + DuckDB backend and a Next.js dashboard.

## Structure

- `apps/api`: FastAPI ingestion + analytics
- `apps/web`: Next.js 14 App Router UI
- `data`: local DuckDB file in development

## Run locally

### Backend

```bash
cd apps/api
uv venv
source .venv/bin/activate
uv pip install -r <(uv pip compile pyproject.toml)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
pnpm install
pnpm dev
```

Open `http://localhost:3000` for the UI. Set `NEXT_PUBLIC_API_BASE` if the API runs elsewhere.

## Screenshots

- Landing / Import: _TBD_
- Dashboard: _TBD_
- Explorer: _TBD_
- Reports: _TBD_
