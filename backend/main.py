"""PSXviewAI FastAPI backend — live data from psxdata package.

Start:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Tuple

from data import ANNOUNCEMENTS as MOCK_ANNOUNCEMENTS, SOURCES as MOCK_SOURCES, build_companies
from news_service import process_pipeline_news
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("psxviewai")

app = FastAPI(title="PSXviewAI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:4173", "http://127.0.0.1:4173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Simple TTL cache: refresh companies every 15 min (live quotes are cached by
# psxdata itself for 15 min on disk, so this is just an extra in-process layer)
# ---------------------------------------------------------------------------
_CACHE: Dict[str, Any] = {
    "companies": [],
    "announcements": [],
    "sources": [],
    "ts": 0.0,
    "news_ts": 0.0,
}
CACHE_TTL = 15 * 60   # seconds
NEWS_CACHE_TTL = 10 * 60  # 10 minutes


def get_companies() -> List[Dict]:
    now = time.time()
    if not _CACHE["companies"] or now - _CACHE["ts"] > CACHE_TTL:
        log.info("Refreshing company data from psxdata …")
        companies = build_companies()
        _CACHE["companies"] = companies
        _CACHE["ts"] = now
        log.info("Done — %d companies loaded", len(companies))
    return _CACHE["companies"]


def get_news() -> Tuple[List[Dict], List[Dict]]:
    now = time.time()
    if not _CACHE["announcements"] or now - _CACHE["news_ts"] > NEWS_CACHE_TTL:
        log.info("Refreshing news from economic pipeline …")
        announcements, sources = process_pipeline_news()
        if not announcements:
            log.warning("No pipeline news items loaded; falling back to mock news.")
            announcements, sources = MOCK_ANNOUNCEMENTS, MOCK_SOURCES
        _CACHE["announcements"] = announcements
        _CACHE["sources"] = sources
        _CACHE["news_ts"] = now
        log.info("Loaded %d real announcements from intelligence pipeline", len(announcements))
    return _CACHE["announcements"], _CACHE["sources"]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def _warmup():
    """Pre-fetch on startup so the first request isn't slow."""
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_companies)
    await loop.run_in_executor(None, get_news)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "cached_at": _CACHE["ts"],
        "news_cached_at": _CACHE["news_ts"],
        "news_count": len(_CACHE["announcements"]),
    }


@app.get("/api/companies")
def companies():
    return get_companies()


@app.get("/api/announcements")
def announcements():
    ann, _ = get_news()
    return ann


@app.get("/api/sources")
def sources():
    _, src = get_news()
    return src


@app.post("/api/news/refresh")
def refresh_news():
    """Manually invalidate news cache and re-read pipeline snapshots."""
    _CACHE["news_ts"] = 0.0
    ann, src = get_news()
    return {"refreshed": True, "count": len(ann)}


@app.get("/api/market")
def market():
    """Single round-trip bundle the frontend uses on load."""
    companies = get_companies()
    announcements, sources = get_news()
    as_of = next((c.get("asOf") for c in companies if c.get("asOf")), "")
    return {
        "companies": companies,
        "announcements": announcements,
        "sources": sources,
        "asOf": as_of,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
