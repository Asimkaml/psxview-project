"""Unit tests for the pure DCF math helpers.

The numerical checks for KOHC and DGKC mirror the HTML tool that originally
shipped with the project. Rounding is used to keep the tests robust to tiny
floating‑point differences.
"""
from __future__ import annotations

import math

import dcf


def test_required_return_capm():
    """Basic CAPM sanity check."""

    assert dcf.required_return(11.0, 6.0, 1.0) == 17.0
    assert dcf.required_return(10.0, 5.0, 1.2) == 16.0


def test_kohc_valuation_matches_reference():
    """KOHC example from the HTML tool: 5‑year two‑stage DCF.

    Inputs roughly match the equity research demo in the original repo.
    """

    eps = 22.1
    price = 97.42
    rf = 11.0
    erp = 6.0
    beta = 1.0
    years = 5
    growth = 8.0
    terminal = 3.5

    result = dcf.compute(
        eps=eps,
        price=price,
        rf_pct=rf,
        erp_pct=erp,
        beta=beta,
        years=years,
        growth_pct=growth,
        terminal_pct=terminal,
    )

    # Required return via CAPM.
    assert math.isclose(result["required_return_pct"], 17.0)

    # Fair value should be about Rs 201 per share.
    assert round(result["fair_value"]) == 201

    # Upside should be a bit above 100% at this price.
    assert 100 < result["upside_pct"] < 120

    # Sensitivity grid: 19 points for growth from 3.5% to 12.5% in 0.5‑pt steps.
    sens = result["sensitivity"]
    assert len(sens["growth_pct"]) == 19
    assert len(sens["fair_value"]) == 19
    assert sens["growth_pct"][0] == 3.5
    assert sens["growth_pct"][-1] == 12.5


def test_dgkc_example_and_implied_growth():
    """Another stock (DGKC) – focus on implied growth sign and magnitude.

    Exact market parameters are not important here; what matters is that the
    implied growth is negative (price below simple DCF) and within a sane
    range, which acts as a regression test for the bisection logic.
    """

    eps = 9.8
    price = 44.25
    rf = 11.0
    erp = 6.0
    beta = 1.1
    years = 5
    growth = 6.0
    terminal = 3.5

    k = dcf.required_return(rf, erp, beta)
    fair = dcf.dcf_valuation(eps, k, years, growth, terminal)
    assert fair > 0

    imp = dcf.implied_growth(eps, price, k, years, terminal)
    # Should find a real root with a mildly negative growth rate.
    assert imp is not None
    assert -30.0 < imp < 0.0


def test_implied_growth_none_when_out_of_bounds():
    """If the target price is too high even at 500% growth, we return None."""

    eps = 5.0
    price = 10_000.0
    rf = 10.0
    erp = 5.0
    beta = 1.0
    years = 5
    terminal = 3.0

    k = dcf.required_return(rf, erp, beta)
    imp = dcf.implied_growth(eps, price, k, years, terminal)
    assert imp is None


def test_compute_rejects_non_positive_inputs():
    """Top‑level compute should enforce basic positivity constraints."""

    try:
        dcf.compute(
            eps=0.0,
            price=100.0,
            rf_pct=10.0,
            erp_pct=5.0,
            beta=1.0,
            years=5,
            growth_pct=5.0,
            terminal_pct=2.0,
        )
    except ValueError as e:
        assert "eps and price must be positive" in str(e)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ValueError for non‑positive eps")
