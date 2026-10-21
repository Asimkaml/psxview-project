# PSXviewAI — FastAPI backend

Serves the prototype market data the React frontend consumes. Data + the
seeded PRNG are in `data.py`; endpoints are in `main.py`.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
# or:  python main.py
```

API will be at http://localhost:8000. The Vite dev server proxies `/api/*`
here, so the frontend calls `/api/market` and it just works.

## Endpoints

- `GET /api/health` — `{ "status": "ok" }`
- `GET /api/companies` — company list (symbol, price, volume, 90-point series, eps)
- `GET /api/announcements` — announcement list
- `GET /api/sources` — per-announcement source records + AI confidence
- `GET /api/market` — all of the above in one call (used by the frontend on load)

Interactive docs: http://localhost:8000/docs
