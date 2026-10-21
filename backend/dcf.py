"""Reverse + forward DCF. Pure functions, no web code. Port of the HTML tool's math."""
from __future__ import annotations

REVERSE_TERMINAL = 0.035   # the HTML tool fixes terminal growth at 3.5% for the reverse solve


def required_return(rf: float, erp: float, beta: float) -> float:
    """CAPM. All inputs as fractions (0.11 = 11%)."""
    return rf + beta * erp


def dcf_value(fcf0: float, g: float, r: float, g_term: float, years: int) -> float:
    """Fair value per share: PV of `years` of growing cash flow + PV of terminal value."""
    if r <= g_term:
        raise ValueError("required return must be higher than terminal growth")
    pv, fcf_n = 0.0, fcf0
    for t in range(1, years + 1):
        fcf_n = fcf0 * (1 + g) ** t
        pv += fcf_n / (1 + r) ** t
    terminal = fcf_n * (1 + g_term) / (r - g_term)
    return pv + terminal / (1 + r) ** years


def solve_implied_growth(price: float, fcf0: float, r: float, years: int,
                         g_term: float = REVERSE_TERMINAL) -> float | None:
    """Growth rate the market price already assumes. None = needs more than 500%."""
    if fcf0 <= 0 or price <= 0 or r <= g_term:
        return None
    if dcf_value(fcf0, 5.0, r, g_term, years) < price:
        return None
    lo, hi = -0.99, 5.0
    for _ in range(200):                      # bisection: halve the range each loop
        mid = (lo + hi) / 2
        if dcf_value(fcf0, mid, r, g_term, years) < price:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    return (lo + hi) / 2


def sensitivity(fcf0: float, price: float, r: float, g_term: float, years: int):
    """Upside % at growth 0,2,4..36 (for the chart)."""
    growth = list(range(0, 37, 2))
    upside = [(dcf_value(fcf0, g / 100, r, g_term, years) - price) / price * 100 for g in growth]
    return {"growth_pct": growth, "upside_pct": upside}


def compute(*, eps: float, price: float, rf_pct: float, erp_pct: float, beta: float,
            years: int, growth_pct: float, terminal_pct: float) -> dict:
    r = required_return(rf_pct / 100, erp_pct / 100, beta)
    g_term = terminal_pct / 100
    if r <= g_term:
        raise ValueError("required return must be higher than terminal growth")
    implied = solve_implied_growth(price, eps, r, years)
    fair = dcf_value(eps, growth_pct / 100, r, g_term, years)
    return {
        "required_return_pct": r * 100,
        "implied_growth_pct": None if implied is None else implied * 100,
        "fair_value": fair,
        "upside_pct": (fair - price) / price * 100,
        "sensitivity": sensitivity(eps, price, r, g_term, years),
    }