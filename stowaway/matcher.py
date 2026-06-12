"""Phase 2a — VALIDATION (internal truth).

Deterministic line-level matching of invoice <-> load record <-> POD.
No LLM anywhere in this file, on purpose: money math must be reproducible.
Tolerances are explicit and configurable. Every flag carries evidence.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import (
    Evidence,
    Flag,
    ImpactKind,
    Invoice,
    LoadRecord,
    PodExtract,
    Severity,
)


@dataclass
class Tolerances:
    linehaul_pct: float = 0.01          # 1% variance allowed
    linehaul_floor_cents: int = 2500    # or $25, whichever is greater
    pod_signature_legibility_min: float = 0.5


def _money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def match_invoice(
    invoice: Invoice,
    loads: dict[str, LoadRecord],
    pods: dict[str, PodExtract],
    tol: Tolerances | None = None,
) -> list[Flag]:
    """Internal 3-way match for a single invoice. Returns flags (empty = clean so far)."""
    tol = tol or Tolerances()
    flags: list[Flag] = []

    load = loads.get(invoice.load_id)
    if load is None:
        flags.append(Flag(
            rule="UNKNOWN_LOAD",
            severity=Severity.CRITICAL,
            impact_kind=ImpactKind.AT_RISK,
            dollar_impact_cents=invoice.total_cents,
            confidence=1.0,
            summary=f"Invoice references load {invoice.load_id} which does not exist in the TMS.",
            invoice_id=invoice.invoice_id,
            load_id=invoice.load_id,
            evidence=[Evidence("field", f"load_id={invoice.load_id} not found in load table")],
        ))
        return flags  # nothing else can be checked without a load record

    # -- linehaul variance ---------------------------------------------------
    billed_linehaul = sum(l.amount_cents for l in invoice.lines_for("LINEHAUL"))
    allowed_var = max(int(load.agreed_linehaul_cents * tol.linehaul_pct), tol.linehaul_floor_cents)
    delta = billed_linehaul - load.agreed_linehaul_cents
    if delta > allowed_var:
        flags.append(Flag(
            rule="LINEHAUL_VARIANCE",
            severity=Severity.MEDIUM,
            impact_kind=ImpactKind.LEAKAGE,
            dollar_impact_cents=delta,
            confidence=1.0,
            summary=(
                f"Linehaul billed {_money(billed_linehaul)} vs agreed "
                f"{_money(load.agreed_linehaul_cents)} (tolerance {_money(allowed_var)})."
            ),
            invoice_id=invoice.invoice_id,
            load_id=load.load_id,
            evidence=[
                Evidence("field", f"rate confirmation: agreed_linehaul={_money(load.agreed_linehaul_cents)}"),
                Evidence("computation", f"delta={_money(delta)} > tolerance={_money(allowed_var)}"),
            ],
        ))

    # -- accessorials ---------------------------------------------------------
    allowed = {a.code: a for a in load.accessorials_allowed}
    seen_codes: dict[str, int] = {}
    for line in invoice.lines:
        if line.code in ("LINEHAUL", "FSC"):
            continue
        seen_codes[line.code] = seen_codes.get(line.code, 0) + 1
        allowance = allowed.get(line.code)
        if allowance is None:
            flags.append(Flag(
                rule="UNAUTHORIZED_ACCESSORIAL",
                severity=Severity.MEDIUM,
                impact_kind=ImpactKind.LEAKAGE,
                dollar_impact_cents=line.amount_cents,
                confidence=1.0,
                summary=f"Accessorial '{line.code}' ({line.description}) not in agreed schedule for this load.",
                invoice_id=invoice.invoice_id,
                load_id=load.load_id,
                evidence=[Evidence(
                    "field",
                    f"allowed accessorials: {sorted(allowed) or 'none'}; billed: {line.code} {_money(line.amount_cents)}",
                )],
            ))
        elif line.amount_cents > allowance.max_cents:
            over = line.amount_cents - allowance.max_cents
            flags.append(Flag(
                rule="ACCESSORIAL_OVER_CAP",
                severity=Severity.MEDIUM,
                impact_kind=ImpactKind.LEAKAGE,
                dollar_impact_cents=over,
                confidence=1.0,
                summary=f"'{line.code}' billed {_money(line.amount_cents)} exceeds cap {_money(allowance.max_cents)}.",
                invoice_id=invoice.invoice_id,
                load_id=load.load_id,
                evidence=[Evidence("computation", f"over cap by {_money(over)}")],
            ))
    for code, n in seen_codes.items():
        if n > 1:
            dup_total = sum(l.amount_cents for l in invoice.lines_for(code)[1:])
            flags.append(Flag(
                rule="DUPLICATE_ACCESSORIAL",
                severity=Severity.MEDIUM,
                impact_kind=ImpactKind.LEAKAGE,
                dollar_impact_cents=dup_total,
                confidence=1.0,
                summary=f"Accessorial '{code}' appears {n}x on one invoice.",
                invoice_id=invoice.invoice_id,
                load_id=load.load_id,
                evidence=[Evidence("field", f"{n} lines with code={code}")],
            ))

    # -- POD (the atoms part) --------------------------------------------------
    pod = pods.get(invoice.load_id)
    if pod is None or not pod.present:
        flags.append(Flag(
            rule="POD_MISSING",
            severity=Severity.HIGH,
            impact_kind=ImpactKind.AT_RISK,
            dollar_impact_cents=invoice.total_cents,
            confidence=1.0,
            summary="No proof-of-delivery on file. Invoice cannot clear to billing.",
            invoice_id=invoice.invoice_id,
            load_id=load.load_id,
            evidence=[Evidence("pod", "no POD document matched to this load")],
        ))
    else:
        if not pod.signature_present:
            flags.append(Flag(
                rule="POD_SIGNATURE_MISSING",
                severity=Severity.HIGH,
                impact_kind=ImpactKind.AT_RISK,
                dollar_impact_cents=invoice.total_cents,
                confidence=0.95,
                summary="POD scan has no receiver signature.",
                invoice_id=invoice.invoice_id,
                load_id=load.load_id,
                evidence=[Evidence("pod", "vision model: signature_present=false")],
            ))
        elif pod.signature_legibility < Tolerances().pod_signature_legibility_min:
            flags.append(Flag(
                rule="POD_ILLEGIBLE",
                severity=Severity.HIGH,
                impact_kind=ImpactKind.AT_RISK,
                dollar_impact_cents=invoice.total_cents,
                confidence=0.8,
                summary=f"POD signature present but illegible (score {pod.signature_legibility:.2f}).",
                invoice_id=invoice.invoice_id,
                load_id=load.load_id,
                evidence=[Evidence("pod", f"legibility={pod.signature_legibility:.2f} < 0.50")],
            ))
        if pod.present and pod.consignee_name and load.consignee:
            if _normalize(pod.consignee_name) != _normalize(load.consignee):
                flags.append(Flag(
                    rule="CONSIGNEE_MISMATCH",
                    severity=Severity.HIGH,
                    impact_kind=ImpactKind.AT_RISK,
                    dollar_impact_cents=invoice.total_cents,
                    confidence=0.85,
                    summary=(
                        f"POD signed at '{pod.consignee_name}' but load consignee is "
                        f"'{load.consignee}'. Possibly the wrong document attached."
                    ),
                    invoice_id=invoice.invoice_id,
                    load_id=load.load_id,
                    evidence=[
                        Evidence("pod", f"POD consignee: {pod.consignee_name}"),
                        Evidence("field", f"TMS consignee: {load.consignee}"),
                    ],
                ))

    return flags


def find_duplicate_billing(invoices: list[Invoice]) -> list[Flag]:
    """Cross-invoice check: the same load billed more than once."""
    flags: list[Flag] = []
    by_load: dict[str, list[Invoice]] = {}
    for inv in invoices:
        by_load.setdefault(inv.load_id, []).append(inv)
    for load_id, group in by_load.items():
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda i: (i.invoice_date, i.invoice_id))
        for dup in group[1:]:
            flags.append(Flag(
                rule="DUPLICATE_BILLING",
                severity=Severity.CRITICAL,
                impact_kind=ImpactKind.LEAKAGE,
                dollar_impact_cents=dup.total_cents,
                confidence=1.0,
                summary=(
                    f"Load {load_id} already billed on invoice {group[0].invoice_id} "
                    f"({group[0].invoice_date}); {dup.invoice_id} is a duplicate."
                ),
                invoice_id=dup.invoice_id,
                load_id=load_id,
                evidence=[Evidence(
                    "field",
                    f"{len(group)} invoices reference load {load_id}: "
                    + ", ".join(i.invoice_id for i in group),
                )],
            ))
    return flags


def _normalize(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())
