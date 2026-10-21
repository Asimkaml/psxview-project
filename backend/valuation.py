"""Valuation endpoints: calculate, save, list, delete, AI explain."""
import json
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

import ai
import dcf
from auth import get_current_user
from db import get_db
from models import SavedValuation, User

router = APIRouter(prefix="/api/valuation", tags=["valuation"])


class ValuationIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    eps: float = Field(gt=0, le=100000)            # EPS or FCF per share, Rs
    price: float = Field(gt=0, le=1000000)         # Rs
    rf_pct: float = Field(ge=5, le=22, default=11)
    erp_pct: float = Field(ge=2, le=14, default=6)
    beta: float = Field(ge=0.3, le=2.5, default=1.0)
    years: int = 5                          # must be 3, 5 or 10 (checked in _run)
    growth_pct: float = Field(ge=0, le=100, default=8)
    terminal_pct: float = Field(ge=0, le=8, default=3.5)


def _run(v: ValuationIn) -> dict:
    if v.years not in (3, 5, 10):
        raise HTTPException(422, "years must be 3, 5 or 10")
    try:
        return dcf.compute(eps=v.eps, price=v.price, rf_pct=v.rf_pct, erp_pct=v.erp_pct,
                           beta=v.beta, years=v.years, growth_pct=v.growth_pct,
                           terminal_pct=v.terminal_pct)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.post("/calculate")
def calculate(v: ValuationIn, user: User = Depends(get_current_user)):
    return _run(v)


@router.post("/saved", status_code=201)
def save(v: ValuationIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = _run(v)          # recompute on the server; never trust numbers from the browser
    row = SavedValuation(user_id=user.id, symbol=v.symbol.upper(), eps=v.eps, price=v.price,
                         inputs_json=v.model_dump_json(),
                         result_json=json.dumps({k: result[k] for k in
                                                 ("required_return_pct", "implied_growth_pct",
                                                  "fair_value", "upside_pct")}))
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.get("/saved")
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(SavedValuation).where(SavedValuation.user_id == user.id)
                      .order_by(SavedValuation.id.desc())).all()
    return [{"id": r.id, "symbol": r.symbol, "created_at": r.created_at.isoformat(),
             "inputs": json.loads(r.inputs_json), "result": json.loads(r.result_json)} for r in rows]


@router.delete("/saved/{item_id}")
def delete_saved(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(SavedValuation, item_id)
    if not row or row.user_id != user.id:      # someone else's row looks like "not found"
        raise HTTPException(404, "Not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


# --- AI explanation (max 10 calls per minute per user, in memory) ---
_calls: dict[int, deque] = defaultdict(deque)


@router.post("/explain")
def explain(v: ValuationIn, user: User = Depends(get_current_user)):
    now = time.time()
    q = _calls[user.id]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= 10:
        raise HTTPException(429, "Slow down: max 10 explanations per minute")
    q.append(now)
    result = _run(v)
    return ai.explain(v.model_dump(), result)