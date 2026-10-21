# PSXviewAI (Phase 1 foundation)

This repository hosts the early foundation for **PSXviewAI**, an evidence-backed
financial research assistant for Pakistan Stock Exchange investors.

This phase focuses on a minimal but real FastAPI backend, a React + Vite +
Tailwind frontend shell, JWT-based authentication, and the core relational
schema for users, companies, instruments, watchlists, holdings, market prices,
news/documents, evidence items, valuations, and research conversations.

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL (SQLite fallback for dev)
- Frontend: React, TypeScript, Vite, Tailwind CSS

## Getting started

1. **Install Node dependencies** (root + frontend):

   ```bash
   npm install
   cd frontend && npm install
   ```

2. **Install Python dependencies** for the backend:

   ```bash
   cd backend
   pip install -e .
   ```

3. **Configure environment**

   Copy `.env.example` to `.env` (not committed) and fill in at least
   `DATABASE_URL` (for a real PostgreSQL instance) and `JWT_SECRET_KEY`. In the
   preview environment, set them via the Secrets panel.

4. **Run database migrations** (uses SQLite fallback if `DATABASE_URL` is not set):

   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Start dev servers** (from repository root):

   ```bash
   npm run dev
   ```

   - Backend: http://localhost:8000 (FastAPI)
   - Frontend: http://localhost:5173 (Vite, proxied `/api` → backend)

## Notes

- Authentication is JWT-based: the frontend stores the access token in
  `localStorage` for now; later phases can harden this.
- The schema is created via Alembic and modeled in `backend/app/db/models/*`.
- Many application features (portfolio flows, news ingestion, valuation engine,
  AI assistant, and complete testing) are intentionally left for later phases.
