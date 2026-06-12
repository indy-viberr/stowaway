"""Phase 2b — VALIDATION (external truth).

The thesis of this project: half the truth an invoice must match lives
OUTSIDE your four walls, and it changes weekly. These checks validate against
the live world via Tavily:

  1. Carrier identity   — FMCSA SAFER: does this MC number exist, is its
                          authority active, does the legal name match?
                          (catches phantom carriers & double-brokering)
  2. Fuel surcharge     — DOE weekly on-highway diesel index: was the FSC
                          computed from THIS week's price?
  3. Vendor dossier     — Tavily /research deep-dive, escalated only for
                          invoices that trip >= 2 flags. Cited risk report.

Replay mode reads committed fixtures. Live mode (Mikey: task #1 in the
handoff) hits Tavily and records fixtures as it goes.
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Any

from .models import Evidence, Flag, ImpactKind, Invoice, LoadRecord, Severity
from .replay import FixtureStore, ReplayMissError

FMCSA_NS = "fmcsa"
DOE_NS = "doe_diesel"
DOSSIER_NS = "dossiers"

# Contractual FSC schedule: DOE national avg $/gal -> FSC as % of linehaul.
# (In production this is per-contract; one schedule is enough for the demo.)
FSC_SCHEDULE: list[tuple[float, float, float]] = [
    (0.00, 3.25, 0.16),
    (3.25, 3.50, 0.18),
    (3.50, 3.75, 0.20),
    (3.75, 4.00, 0.22),
    (4.00, 4.25, 0.24),
    (4.25, 99.0, 0.26),
]


def fsc_pct_for_price(price: float) -> float:
    for lo, hi, pct in FSC_SCHEDULE:
        if lo <= price < hi:
            return pct
    raise ValueError(f"diesel price {price} outside schedule")


def week_monday(date_iso: str) -> str:
    d = dt.date.fromisoformat(date_iso)
    return (d - dt.timedelta(days=d.weekday())).isoformat()


def _money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


class TruthClient:
    """External-truth checks. mode='replay' (fixtures) or 'live' (Tavily)."""

    def __init__(self, fixtures: FixtureStore, mode: str = "replay"):
        self.fixtures = fixtures
        self.mode = mode
        if mode == "live" and not os.environ.get("TAVILY_API_KEY"):
            raise RuntimeError("live mode requires TAVILY_API_KEY (see .env.example)")

    # ------------------------------------------------------------------ FMCSA
    def carrier_record(self, mc_number: str) -> dict[str, Any]:
        rec = self.fixtures.get(FMCSA_NS, mc_number)
        if rec is not None:
            return rec
        if self.mode == "replay":
            raise ReplayMissError(FMCSA_NS, mc_number)
        rec = self._live_fmcsa_lookup(mc_number)
        self.fixtures.put(FMCSA_NS, mc_number, rec)
        return rec

    def check_carrier(self, invoice: Invoice) -> list[Flag]:
        rec = self.carrier_record(invoice.carrier_mc)
        flags: list[Flag] = []
        cite = rec.get("source", f"fixture:{FMCSA_NS}[{invoice.carrier_mc}]")
        if not rec.get("found"):
            flags.append(Flag(
                rule="PHANTOM_CARRIER",
                severity=Severity.CRITICAL,
                impact_kind=ImpactKind.AT_RISK,
                dollar_impact_cents=invoice.total_cents,
                confidence=0.97,
                summary=f"MC {invoice.carrier_mc} does not exist in FMCSA records. Do not pay.",
                invoice_id=invoice.invoice_id,
                load_id=invoice.load_id,
                evidence=[Evidence("web", f"FMCSA SAFER: no record for MC {invoice.carrier_mc}", cite)],
            ))
            return flags
        if rec.get("authority") != "ACTIVE":
            flags.append(Flag(
                rule="AUTHORITY_REVOKED",
                severity=Severity.CRITICAL,
                impact_kind=ImpactKind.AT_RISK,
                dollar_impact_cents=invoice.total_cents,
                confidence=0.95,
                summary=(
                    f"MC {invoice.carrier_mc} authority is {rec.get('authority')} "
                    f"— carrier was not authorized to haul this load."
                ),
                invoice_id=invoice.invoice_id,
                load_id=invoice.load_id,
                evidence=[Evidence("web", f"FMCSA authority status: {rec.get('authority')}", cite)],
            ))
        legal = rec.get("legal_name", "")
        if legal and _normalize(legal) != _normalize(invoice.carrier_name):
            flags.append(Flag(
                rule="CARRIER_NAME_MISMATCH",
                severity=Severity.CRITICAL,
                impact_kind=ImpactKind.AT_RISK,
                dollar_impact_cents=invoice.total_cents,
                confidence=0.85,
                summary=(
                    f"Invoice says '{invoice.carrier_name}' but MC {invoice.carrier_mc} "
                    f"belongs to '{legal}'. Classic double-brokering signature."
                ),
                invoice_id=invoice.invoice_id,
                load_id=invoice.load_id,
                evidence=[
                    Evidence("field", f"invoice carrier_name: {invoice.carrier_name}"),
                    Evidence("web", f"FMCSA legal name for MC {invoice.carrier_mc}: {legal}", cite),
                ],
            ))
        return flags

    # -------------------------------------------------------------- DOE fuel
    def diesel_price(self, week_monday_iso: str) -> float:
        rec = self.fixtures.get(DOE_NS, week_monday_iso)
        if rec is not None:
            return float(rec["price"])
        if self.mode == "replay":
            raise ReplayMissError(DOE_NS, week_monday_iso)
        rec = self._live_doe_lookup(week_monday_iso)
        self.fixtures.put(DOE_NS, week_monday_iso, rec)
        return float(rec["price"])

    def check_fuel_surcharge(self, invoice: Invoice, load: LoadRecord) -> list[Flag]:
        fsc_lines = invoice.lines_for("FSC")
        if not fsc_lines:
            return []
        billed_fsc = sum(l.amount_cents for l in fsc_lines)
        week = week_monday(load.pickup_date)
        price = self.diesel_price(week)
        expected = round(load.agreed_linehaul_cents * fsc_pct_for_price(price))
        delta = billed_fsc - expected
        if delta <= max(int(expected * 0.02), 500):   # 2% / $5 rounding grace
            return []
        # Which week's price WOULD produce the billed amount? (Story evidence.)
        used_week = self._reverse_lookup_week(billed_fsc, load.agreed_linehaul_cents)
        ev = [
            Evidence("web", f"DOE on-highway diesel, week of {week}: ${price:.3f}/gal",
                     f"fixture:{DOE_NS}[{week}]" if self.mode == "replay" else "https://www.eia.gov/petroleum/gasdiesel/"),
            Evidence("computation",
                     f"expected FSC = {_money(load.agreed_linehaul_cents)} x "
                     f"{fsc_pct_for_price(price):.0%} = {_money(expected)}; billed {_money(billed_fsc)}"),
        ]
        summary = f"Fuel surcharge overbilled by {_money(delta)} vs this week's DOE index."
        if used_week:
            summary += f" Billed amount matches the week of {used_week} — a stale, higher price."
            ev.append(Evidence("computation", f"billed FSC reverse-matches DOE week {used_week}"))
        return [Flag(
            rule="STALE_FUEL_WEEK",
            severity=Severity.MEDIUM,
            impact_kind=ImpactKind.LEAKAGE,
            dollar_impact_cents=delta,
            confidence=0.9,
            summary=summary,
            invoice_id=invoice.invoice_id,
            load_id=load.load_id,
            evidence=ev,
        )]

    def _reverse_lookup_week(self, billed_fsc: int, linehaul: int) -> str | None:
        for week, rec in self.fixtures.load(DOE_NS).items():
            pct = fsc_pct_for_price(float(rec["price"]))
            if abs(round(linehaul * pct) - billed_fsc) <= 100:
                return week
        return None

    # ------------------------------------------------------------- dossiers
    def vendor_dossier(self, invoice: Invoice) -> str:
        """Escalation: full cited risk report on a vendor that tripped >= 2 flags.
        Live mode uses Tavily /research (their flagship 2026 endpoint)."""
        key = invoice.carrier_mc
        rec = self.fixtures.get(DOSSIER_NS, key)
        if rec is not None:
            return rec["report_md"]
        if self.mode == "replay":
            raise ReplayMissError(DOSSIER_NS, key)
        rec = self._live_dossier(invoice)
        self.fixtures.put(DOSSIER_NS, key, rec)
        return rec["report_md"]

    # ----------------------------------------------------- live impls
    # Implemented in tavily_live.py (stdlib urllib; imported only in live mode).
    # Written key-ready but not yet run against the live API — Mikey: see the
    # VERIFY markers in tavily_live.py before trusting parses.
    def _live_fmcsa_lookup(self, mc_number: str) -> dict[str, Any]:
        from . import tavily_live
        return tavily_live.fmcsa_lookup(mc_number)

    def _live_doe_lookup(self, week_monday_iso: str) -> dict[str, Any]:
        from . import tavily_live
        return tavily_live.doe_diesel_lookup(week_monday_iso)

    def _live_dossier(self, invoice: Invoice) -> dict[str, Any]:
        from . import tavily_live
        return tavily_live.research_dossier(invoice.carrier_name, invoice.carrier_mc)


def _normalize(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())
