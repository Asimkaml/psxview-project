"""Pure DCF valuation math used by the PSXviewAI backend.

This module is intentionally free of FastAPI / database imports so that it can
be reused from both route handlers and tests without side‑effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class DcfInputs:
    """Canonical input bundle for the DCF functions.

    All percentages are passed in *percentage* form (e.g. 11 for 11%), not
    decimals. Years is the explicit forecast period.
    """

    eps: float
    price: float
    rf_pct: float
    erp_pct: float
    beta: float
    years: int
    growth_pct: float
    terminal_pct: float


def required_return(rf_pct: float, erp_pct: float, beta: float) -> float:
    """CAPM required return in percentage form.

    k = rf + beta * ERP
    """

    if beta < 0:
        raise ValueError("beta must be non‑negative")
    return rf_pct + beta * erp_pct


def _two_stage_pv(
    eps: float,
    k_pct: float,
    years: int,
    growth_pct: float,
    terminal_pct: float,
) -> float:
    """Present value per share of a two‑stage growing cash‑flow stream.

    - `eps` is the most recent per‑share cash flow (EPS / FCF per share).
    - `k_pct` is the required return in percent.
    - `growth_pct` is the explicit forecast growth rate for the first
      `years` periods.
    - `terminal_pct` is the perpetual terminal growth rate used in the
      Gordon Growth leg.

    Both stages are standard textbook formulas:
    * Stage 1: discount each explicitly‑forecast cash flow.
    * Stage 2: Gordon Growth, based on year‑`years` cash flow growing at
      `terminal_pct` from then on.
    """

    if years <= 0:
        raise ValueError("years must be positive")

    k = k_pct / 100.0
    g = growth_pct / 100.0
    g_t = terminal_pct / 100.0

    if k <= g_t:
        raise ValueError("required return must be above terminal growth")

    # Forecast EPS for each explicit year and discount back.
    pv = 0.0
    eps_t = eps
    for t in range(1, years + 1):
        eps_t *= 1.0 + g
        pv += eps_t / (1.0 + k) ** t

    # Gordon Growth terminal value at the end of the explicit horizon.
    cf_terminal = eps_t * (1.0 + g_t)
    terminal_value = cf_terminal / (k - g_t)
    pv += terminal_value / (1.0 + k) ** years

    return pv


def dcf_valuation(
    eps: float,
    k_pct: float,
    years: int,
    growth_pct: float,
    terminal_pct: float,
) -> float:
    """Wrapper around :func:`_two_stage_pv`.

    Kept as a separate public function so tests can depend on this name.
    """

    return _two_stage_pv(eps=eps, k_pct=k_pct, years=years, growth_pct=growth_pct, terminal_pct=terminal_pct)


def implied_growth(
    eps: float,
    price: float,
    k_pct: float,
    years: int,
    terminal_pct: float,
    *,
    min_growth_pct: float = -50.0,
    max_growth_pct: float = 500.0,
    tol: float = 1e-4,
    max_iter: int = 64,
) -> Optional[float]:
    """Implied *explicit* growth rate that matches the current price.

    Uses a bisection search between ``min_growth_pct`` and
    ``max_growth_pct``. Percentages are in percentage form. Returns

    - a growth rate in percent, if a solution is found inside the bounds; or
    - ``None`` if even the upper bound still yields a value below the price
      ("more than 500%" growth required) or the lower bound PV is already
      above the price.
    """

    if price <= 0:
        raise ValueError("price must be positive")

    low, high = min_growth_pct, max_growth_pct
    pv_low = dcf_valuation(eps, k_pct, years, low, terminal_pct)
    pv_high = dcf_valuation(eps, k_pct, years, high, terminal_pct)

    # If the curve does not bracket the target price inside [low, high], we
    # signal that we don't have a meaningful implied rate.
    if (pv_low - price) * (pv_high - price) >= 0:
        return None

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        pv_mid = dcf_valuation(eps, k_pct, years, mid, terminal_pct)
        diff = pv_mid - price
        if abs(diff) < tol:
            return mid
        # Maintain the bracket where the sign flips.
        if (pv_low - price) * diff < 0:
            high = mid
            pv_high = pv_mid
        else:
            low = mid
            pv_low = pv_mid

    return 0.5 * (low + high)


def sensitivity_grid(inp: DcfInputs) -> Dict[str, List[float]]:
    """Sensitivity of fair value to the explicit growth rate.

    We vary growth from ``growth_pct - 4.5`` to ``growth_pct + 4.5`` in
    0.5‑percentage‑point steps. For the default 8% this yields 19 points,
    which is what the tests expect.
    """

    k = required_return(inp.rf_pct, inp.erp_pct, inp.beta)

    step = 0.5
    half_span = 4.5
    start = inp.growth_pct - half_span
    stop = inp.growth_pct + half_span

    growth_values: List[float] = []
    fair_values: List[float] = []

    g = start
    # Use an index counter instead of comparing floats directly.
    while g <= stop + 1e-9:
        # Growth cannot be negative in this grid; clamp at 0.
        g_eff = max(0.0, g)
        fv = dcf_valuation(inp.eps, k, inp.years, g_eff, inp.terminal_pct)
        growth_values.append(round(g_eff, 2))
        fair_values.append(fv)
        g += step

    return {"growth_pct": growth_values, "fair_value": fair_values}


def compute(
    *,
    eps: float,
    price: float,
    rf_pct: float,
    erp_pct: float,
    beta: float,
    years: int,
    growth_pct: float,
    terminal_pct: float,
) -> Dict[str, object]:
    """Top‑level helper mirroring the shape the API layer expects.

    Returns a dict so that FastAPI can JSON‑serialize it directly.
    """

    if eps <= 0 or price <= 0:
        raise ValueError("eps and price must be positive")

    k = required_return(rf_pct, erp_pct, beta)
    fair = dcf_valuation(eps, k, years, growth_pct, terminal_pct)

    # Implied growth can legitimately be None when the current price implies
    # extreme optimism ("more than 500%" growth).
    implied = implied_growth(eps, price, k, years, terminal_pct)

    upside_pct = (fair / price - 1.0) * 100.0

    sens = sensitivity_grid(
        DcfInputs(
            eps=eps,
            price=price,
            rf_pct=rf_pct,
            erp_pct=erp_pct,
            beta=beta,
            years=years,
            growth_pct=growth_pct,
            terminal_pct=terminal_pct,
        )
    )

    return {
        "required_return_pct": k,
        "implied_growth_pct": implied,
        "fair_value": fair,
        "upside_pct": upside_pct,
        "sensitivity": sens,
    }
