"""Core data model. Plain stdlib dataclasses — the deterministic spine of the system.

All money is integer cents. All dates are ISO strings (YYYY-MM-DD).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"   # do not pay; likely fraud
    HIGH = "high"           # hold; evidence problem
    MEDIUM = "medium"       # overbilling; recoverable
    LOW = "low"             # informational


class ImpactKind(str, Enum):
    LEAKAGE = "leakage"     # dollars overbilled (recoverable)
    AT_RISK = "at_risk"     # full payment should not go out as-is


@dataclass
class AccessorialAllowance:
    code: str               # e.g. "DET", "LUMPER", "TONU"
    max_cents: int


@dataclass
class LoadRecord:
    """Source of truth from the TMS: what we agreed to."""
    load_id: str
    lane: str                       # "Laredo, TX -> Memphis, TN"
    pickup_date: str
    carrier_mc: str
    carrier_name: str
    agreed_linehaul_cents: int
    consignee: str
    accessorials_allowed: list[AccessorialAllowance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LoadRecord":
        d = dict(d)
        d["accessorials_allowed"] = [
            AccessorialAllowance(**a) for a in d.get("accessorials_allowed", [])
        ]
        return cls(**d)


@dataclass
class InvoiceLine:
    code: str                       # LINEHAUL | FSC | DET | LUMPER | ...
    description: str
    amount_cents: int


@dataclass
class Invoice:
    """What the carrier billed us."""
    invoice_id: str
    invoice_date: str
    carrier_mc: str
    carrier_name: str
    load_id: str
    lines: list[InvoiceLine] = field(default_factory=list)

    @property
    def total_cents(self) -> int:
        return sum(l.amount_cents for l in self.lines)

    def lines_for(self, code: str) -> list[InvoiceLine]:
        return [l for l in self.lines if l.code == code]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Invoice":
        d = dict(d)
        d["lines"] = [InvoiceLine(**l) for l in d.get("lines", [])]
        return cls(**d)


@dataclass
class PodExtract:
    """What the vision model read off the physical proof-of-delivery scan.

    In replay mode these come from fixtures; in live mode from a VLM on
    Nebius Token Factory reading the actual scan image.
    """
    load_id: str
    present: bool
    signature_present: bool = False
    signature_legibility: float = 0.0   # 0..1, model-assessed
    date_legible: bool = False
    consignee_name: str = ""
    doc_quality: float = 0.0            # 0..1 overall scan quality

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PodExtract":
        return cls(**d)


@dataclass
class Evidence:
    """One verifiable item supporting a flag. Citations make flags auditable."""
    kind: str                      # "field" | "web" | "pod" | "computation"
    detail: str
    citation: str = ""             # URL or fixture ref for web-truth evidence


@dataclass
class Flag:
    rule: str
    severity: Severity
    impact_kind: ImpactKind
    dollar_impact_cents: int
    confidence: float              # 0..1
    summary: str
    invoice_id: str
    load_id: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class InvoiceVerdict:
    invoice: Invoice
    flags: list[Flag] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.flags

    @property
    def worst_severity(self) -> Severity | None:
        if not self.flags:
            return None
        order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        for s in order:
            if any(f.severity == s for f in self.flags):
                return s
        return None
