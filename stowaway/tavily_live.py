"""Live Tavily client. Stdlib urllib only — replay mode never imports this.

STATUS: written key-ready but NOT yet run against the live API (no key in this
environment). Mikey: verify request/response shapes against docs.tavily.com
before trusting parses; the seams to check are marked VERIFY.

Failure-mode handling (deliberate):
- timeouts: advanced-depth p95 is seconds — we time out and retry once at
  basic depth rather than hang the audit loop.
- stale URLs: Tavily's index can return dead links; we HEAD-check before
  extracting and skip 4xx/5xx targets.
- parse failures: a lookup that can't be parsed raises TruthLookupError.
  An audit tool must fail closed and loudly — "couldn't verify" is an answer,
  "silently assumed fine" is a bug.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

API = "https://api.tavily.com"


class TruthLookupError(RuntimeError):
    """External truth could not be established. Route to a human; never assume."""


def _post(path: str, payload: dict[str, Any], timeout: float = 15.0) -> dict[str, Any]:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise TruthLookupError("TAVILY_API_KEY not set")
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise TruthLookupError(f"Tavily {path} HTTP {e.code}: {e.read()[:200]!r}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise TruthLookupError(f"Tavily {path} unreachable/timeout: {e}") from e


def _url_alive(url: str, timeout: float = 5.0) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


def search(query: str, *, depth: str = "advanced", include_domains: list[str] | None = None,
           max_results: int = 5) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "query": query, "search_depth": depth, "max_results": max_results,
        "include_raw_content": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    try:
        return _post("/search", payload)
    except TruthLookupError:
        if depth == "advanced":           # degrade once, visibly
            return _post("/search", {**payload, "search_depth": "basic"})
        raise


def extract(url: str) -> str:
    if not _url_alive(url):
        raise TruthLookupError(f"target URL failed HEAD check (stale index?): {url}")
    res = _post("/extract", {"urls": [url]})
    # VERIFY: response shape — expected {"results": [{"url":..., "raw_content":...}]}
    results = res.get("results") or []
    if not results:
        raise TruthLookupError(f"extract returned nothing for {url}")
    return results[0].get("raw_content", "")


# ----------------------------------------------------------------- FMCSA

_SAFER = "safer.fmcsa.dot.gov"
_RE_LEGAL = re.compile(r"Legal Name[:\s]+([A-Z0-9&.,' -]{3,80})", re.I)
_RE_AUTH = re.compile(r"Operating (?:Authority )?Status[:\s]+([A-Z ]{2,40})", re.I)


def fmcsa_lookup(mc_number: str) -> dict[str, Any]:
    """Carrier identity via FMCSA SAFER. SAFER has no clean public API; this is
    search + extract + regex, and the confidence fields say so honestly."""
    res = search(f'FMCSA SAFER company snapshot "MC-{mc_number}"',
                 include_domains=[_SAFER], max_results=3)
    hits = res.get("results") or []
    safer_hits = [h for h in hits if _SAFER in h.get("url", "")]
    if not safer_hits:
        # No SAFER page surfaced at all. That is *evidence of* nonexistence,
        # not proof — confidence stays below auto-clear thresholds either way.
        return {"found": False, "confidence": 0.8,
                "source": f"tavily:search MC-{mc_number} (no SAFER record surfaced)"}
    url = safer_hits[0]["url"]
    page = extract(url)
    if re.search(r"no records? (?:match|found)", page, re.I):
        return {"found": False, "confidence": 0.95, "source": url}
    legal = _RE_LEGAL.search(page)
    auth = _RE_AUTH.search(page)
    if not legal:
        raise TruthLookupError(f"SAFER page parsed but no legal name found: {url}")
    auth_raw = (auth.group(1).strip().upper() if auth else "UNKNOWN")
    authority = "ACTIVE" if "ACTIVE" in auth_raw else (
        "REVOKED" if ("REVOKED" in auth_raw or "INACTIVE" in auth_raw) else auth_raw)
    return {"found": True, "legal_name": legal.group(1).strip(),
            "authority": authority, "source": url}


# ----------------------------------------------------------------- DOE diesel

_RE_PRICE = re.compile(r"\$?([3-6]\.\d{2,3})\s*(?:/|per)?\s*gal", re.I)


def doe_diesel_lookup(week_monday_iso: str) -> dict[str, Any]:
    """US national average on-highway diesel for the given Monday, via eia.gov."""
    res = search(
        f"EIA weekly retail on-highway diesel price national average week of {week_monday_iso}",
        include_domains=["eia.gov"], max_results=3)
    for hit in res.get("results") or []:
        m = _RE_PRICE.search(hit.get("content", ""))
        if m:
            return {"price": float(m.group(1)), "source": hit["url"]}
    # search snippets failed; try extracting the gasdiesel page itself
    page = extract("https://www.eia.gov/petroleum/gasdiesel/")
    m = _RE_PRICE.search(page)
    if m:
        return {"price": float(m.group(1)),
                "source": "https://www.eia.gov/petroleum/gasdiesel/"}
    raise TruthLookupError(f"could not establish DOE diesel price for {week_monday_iso}")


# ----------------------------------------------------------------- dossier

def research_dossier(carrier_name: str, mc_number: str) -> dict[str, Any]:
    """Cited vendor-risk dossier via Tavily /research (their managed deep-research
    endpoint). VERIFY: request schema against current docs — it's new (Jan 2026).
    Falls back to assembling citations from advanced search if /research errors."""
    prompt = (
        f"Risk assessment of freight carrier '{carrier_name}' (MC {mc_number}): "
        f"entity age and registration state, registered agent address (is it a "
        f"mailbox store?), FMCSA authority history and complaints, litigation, "
        f"connections to other carrier identities. Cite every claim."
    )
    try:
        res = _post("/research", {"query": prompt}, timeout=120.0)
        # VERIFY: response shape — expected a structured report w/ citations
        report = res.get("report") or res.get("answer") or json.dumps(res)[:4000]
        return {"report_md": report}
    except TruthLookupError:
        res = search(f'"{carrier_name}" MC {mc_number} carrier complaints registration',
                     max_results=5)
        lines = [f"**Vendor risk notes — {carrier_name} (MC {mc_number})** "
                 f"*(assembled from search; /research unavailable)*\n"]
        for h in res.get("results") or []:
            lines.append(f"- {h.get('title', 'untitled')}: {h.get('content', '')[:200]} "
                         f"[{h.get('url', '')}]")
        return {"report_md": "\n".join(lines)}
