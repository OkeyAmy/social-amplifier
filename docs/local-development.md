# Local Development Guide

This document describes how to run the Social Amplifier frontend and backend together during development.

## Prerequisites

- **Node.js** 18 or newer
- **pnpm** 8 or newer
- **Python** 3.11 or newer

## Backend (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python main.py
```

The API server listens on `http://localhost:8000` by default. Interactive docs are available at `http://localhost:8000/docs` once the server is running.

## Frontend (Vite React)

```powershell
pnpm install --no-strict-peer-dependencies
if (!(Test-Path .env.local)) { Copy-Item .env.example .env.local }
Add-Content .env.local "VITE_API_BASE_URL=http://localhost:8000"
Add-Content backend/.env "DEFAULT_USER_EMAIL=default@socialamplifier.local"
pnpm dev -- --host
```

The Vite dev server listens on `http://localhost:8080`. The frontend now consumes backend APIs for:

- OAuth connection status (`/api/v1/auth/status`)
- OAuth initiation and disconnect flows (`/api/v1/auth/*`)
- AI content generation (`/api/v1/generate/*`)
- Draft management (`/api/v1/drafts/*`)

## Verification Checklist

1. Visit `http://localhost:8080/connect` to fetch live connection status and launch OAuth flows.
2. Generate content from the landing page and confirm the preview populates from backend responses.
3. Save a draft and open `http://localhost:8080/posts` to confirm it loads from the API.
4. Review API responses via `http://localhost:8000/docs` as needed.
