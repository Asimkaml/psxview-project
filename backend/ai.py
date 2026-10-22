"""AI explanation of a valuation via Gemini REST. Falls back to plain text if AI fails."""
import logging
import time

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
        f"Required return (CAPM): {res['required_return_pct']:.1f}%\n"
        f"Projection years: {inp['years']}\n"
        f"Growth the market price already implies: {implied_txt} per year\n"
        f"User's growth estimate: {inp['growth_pct']}% per year, terminal growth {inp['terminal_pct']}%\n"
        f"Fair value at user's estimate: Rs {res['fair_value']:.0f} ({res['upside_pct']:+.0f}% vs price)\n"
    )


def fallback_text(inp: dict, res: dict) -> str:
    implied = res["implied_growth_pct"]
    a = ("The price needs more than 500% yearly growth to make sense." if implied is None
         else f"The current price already assumes about {implied:.1f}% yearly growth.")
    b = (f"At your {inp['growth_pct']}% estimate, fair value is Rs {res['fair_value']:.0f}, "
         f"which is {abs(res['upside_pct']):.0f}% {'above' if res['upside_pct'] >= 0 else 'below'} the price.")
    return f"{a} {b} Educational only, not advice."


def explain(inp: dict, res: dict) -> dict:
    if not config.GEMINI_API_KEY:
        return {"text": fallback_text(inp, res), "source": "fallback"}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            r = httpx.post(
                URL.format(model=config.GEMINI_MODEL),
                headers={"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": build_prompt(inp, res)}]}],
                    "generationConfig": {
                        "maxOutputTokens": 1200,
                        "thinkingConfig": {"thinkingLevel": "low"},
                    },
                },
                timeout=30,
            )
            r.raise_for_status()
            candidate = r.json()["candidates"][0]
            text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            if not text:
                raise ValueError(f"Gemini returned no text ({candidate.get('finishReason', 'unknown')})")
            return {"text": text, "source": "gemini"}
        except httpx.HTTPStatusError as e:
            last_error = e
            status = e.response.status_code
            log.warning("Gemini request failed with HTTP %s (attempt %s/3)", status, attempt + 1)
            if status != 429 and status < 500:
                break
        except Exception as e:  # network or malformed provider response
            last_error = e
            log.warning("Gemini request failed: %s (attempt %s/3)", type(e).__name__, attempt + 1)
        if attempt < 2:
            time.sleep(attempt + 1)

    log.warning("Using valuation fallback after Gemini failure: %s", type(last_error).__name__)
    return {"text": fallback_text(inp, res), "source": "fallback"}
