"""Probe the live Tavily seams, one at a time, with raw output.

This is a diagnostic, not part of the pipeline. Run it BEFORE trusting live
mode: it shows you exactly what the API returns so you can fix the parse
seams (marked VERIFY in stowaway/tavily_live.py) against reality instead of
guessing.

Usage (from repo root, TAVILY_API_KEY in env or .env):
    python3 scripts/probe_live.py fmcsa 133655        # any real MC number
    python3 scripts/probe_live.py doe                  # current week's diesel
    python3 scripts/probe_live.py dossier "Some Carrier LLC" 133655
    python3 scripts/probe_live.py search "test query"  # raw /search response
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# convenience: read .env if the key isn't exported
if not os.environ.get("TAVILY_API_KEY") and (ROOT / ".env").exists():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from stowaway import tavily_live  # noqa: E402
from stowaway.truth import week_monday  # noqa: E402


def show(label: str, fn, *args):
    print(f"\n=== {label} ===")
    try:
        result = fn(*args)
        print(json.dumps(result, indent=2, default=str)[:3000])
        print("--- PROBE OK")
    except Exception as e:  # noqa: BLE001 — diagnostics want everything
        print(f"--- PROBE FAILED: {type(e).__name__}: {e}")
        print("    (expected on first run — fix the VERIFY seam this exposes)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "fmcsa":
        show(f"FMCSA lookup MC {sys.argv[2]}", tavily_live.fmcsa_lookup, sys.argv[2])
    elif cmd == "doe":
        week = week_monday(dt.date.today().isoformat())
        show(f"DOE diesel, week of {week}", tavily_live.doe_diesel_lookup, week)
    elif cmd == "dossier":
        show(f"dossier {sys.argv[2]}", tavily_live.research_dossier, sys.argv[2], sys.argv[3])
    elif cmd == "search":
        show(f"raw search: {sys.argv[2]}", tavily_live.search, sys.argv[2])
    else:
        sys.exit(f"unknown probe: {cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
