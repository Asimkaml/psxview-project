from __future__ import annotations

import logging
from typing import Any

import requests
from requests import Response
from requests.exceptions import ConnectionError, SSLError, Timeout


RETRYABLE_STATUS_CODES = {502, 504}


def get_with_http_fallback(
    url: str,
    source: dict[str, Any],
    timeout: int,
    headers: dict[str, str] | None = None,
) -> tuple[Response, str, str | None]:
    request_headers = headers or {"User-Agent": source.get("user_agent", "Mozilla/5.0")}
    try:
        response = requests.get(url, headers=request_headers, timeout=timeout)
        response.raise_for_status()
        return response, response.url, None
    except Exception as exc:
        if not should_try_http_fallback(url, exc, source):
            source["_final_url_used"] = url
            raise

        fallback_url = "http://" + url[len("https://") :]
        logging.warning("primary_url failed [%s]: %s", url, exc)
        logging.warning("fallback_url tried [%s]", fallback_url)
        try:
            fallback_timeout = max(2, int(source.get("http_fallback_timeout", timeout)))
            fallback_response = requests.get(
                fallback_url, headers=request_headers, timeout=fallback_timeout
            )
            fallback_response.raise_for_status()
        except Exception as fallback_exc:
            source["_final_url_used"] = fallback_url
            source["_fetch_note"] = "http_fallback_failed"
            logging.warning("fallback failed [%s]: %s", fallback_url, fallback_exc)
            raise fallback_exc from exc
        logging.warning("fallback success [%s]", fallback_url)
        return fallback_response, fallback_response.url, "used_http_fallback"


def should_try_http_fallback(url: str, exc: Exception, source: dict[str, Any]) -> bool:
    if source.get("try_http_fallback", True) is False:
        return False
    return is_retryable_https_failure(url, exc)


def is_retryable_https_failure(url: str, exc: Exception) -> bool:
    if not url.startswith("https://"):
        return False
    if isinstance(exc, (SSLError, Timeout)):
        return True
    response = getattr(exc, "response", None)
    if response is not None and response.status_code in RETRYABLE_STATUS_CODES:
        return True
    message = str(exc).casefold()
    if "failed to resolve" in message or "nameresolutionerror" in message:
        return False
    if isinstance(exc, ConnectionError):
        return "connection refused" in message
    return any(token in message for token in ("ssl", "502", "504", "connection refused", "timed out", "timeout"))
