"""AI explanation of a valuation via Gemini REST. Falls back to plain text if AI fails."""
import logging

import httpx

import config

log = logging.getLogger("psxviewai.ai")

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def build_prompt(inp: dict, res: dict) -> str:
    implied = res["implied_growth_pct"]
    implied_txt = "more than 500%" if implied is None else f"{implied:.1f}%"
    return (
        "You are a careful teaching assistant for retail investors on the Pakistan Stock Exchange.\n"
        "Explain the valuation below in at most 120 words, plain English, no jargon without a short definition.\n"
        "Rules: use ONLY the numbers given. Do NOT say buy, sell or hold. Do NOT predict prices. "
        "Mention one limitation of this method. Finish with: 'Educational only, not advice.'\n\n"
        f"Company: {inp['symbol']}\n"
        f"EPS/FCF per share: Rs {inp['eps']}\nCurrent price: Rs {inp['price']}\n"
        f"Risk-free rate: {inp['rf_pct']:.1f}%\n"
        f"Equity risk premium: {inp['erp_pct']:.1f}%\n"
        f"Beta: {inp['beta']:.2f}\n"
        f"Forecast years: {inp['years']}\n"
        f"Explicit growth assumption: {inp['growth_pct']:.1f}% per year\n"
        f"Terminal growth assumption: {inp['terminal_pct']:.1f}% per year\n"
        f"Required return (CAPM): {res['required_return_pct']:.1f}%\n"
        f"Implied growth baked into price: {implied_txt} per year\n"
        f"DCF fair value per share: Rs {res['fair_value']:.2f}\n"
        f"Upside/downside vs price: {res['upside_pct']:.1f}%\n"
    )


def _fallback_text(inp: dict, res: dict) -> dict:
    implied = res["implied_growth_pct"]
    implied_txt = "more than 500%" if implied is None else f"{implied:.1f}%"
    return {
        "source": "fallback",
        "text": (
            f"This DCF takes Rs {inp['eps']} per share and grows it at {inp['growth_pct']:.1f}% "
            f"for {inp['years']} years, then {inp['terminal_pct']:.1f}% forever. Using a required "
            f"return of {res['required_return_pct']:.1f}%, it estimates fair value around "
            f"Rs {res['fair_value']:.2f} per share, which is {res['upside_pct']:.1f}% versus the "
            f"current price of Rs {inp['price']}. The current price implies {implied_txt} annual "
            "growth. This is a simplified model and small changes in inputs can move the value a lot. "
            "Educational only, not advice."
        ),
    }


def explain(inp: dict, res: dict) -> dict:
    """Ask Gemini to explain the valuation; fall back to safe text on any error."""

    api_key = config.settings.gemini_api_key
    model = config.settings.gemini_model

    if not api_key or not model:
        log.warning("Gemini API key or model missing; using fallback explanation.")
        return _fallback_text(inp, res)

    prompt = build_prompt(inp, res)

    headers = {"x-goog-api-key": api_key}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                ]
            }
        ]
    }

    url = URL.format(model=model)

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, headers=headers, json=body)
        if r.status_code == 404:
            log.error("Gemini model not found (404). Check GEMINI_MODEL setting.")
        r.raise_for_status()
        data = r.json()
        text = "".join(part.get("text", "") for
                        cand in data.get("candidates", [])
                        for part in cand.get("content", {}).get("parts", []))
        if not text.strip():
            raise ValueError("Empty response from Gemini")
        return {"source": "gemini", "text": text}
    except Exception as exc:  # noqa: BLE001
        log.error("Gemini explanation failed, falling back: %s", exc)
        return _fallback_text(inp, res)
