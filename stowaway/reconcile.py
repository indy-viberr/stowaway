"""Phase 3 — RECONCILIATION.

Aggregate verdicts, rank exceptions by dollar impact, attach evidence chains,
render the audit report. Routing (Slack via Composio, Telegram via OpenClaw)
consumes the same ExceptionQueue. The agent never moves money: clean invoices
are *recommended* for billing; every exception goes to a human with receipts.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import Flag, ImpactKind, Invoice, InvoiceVerdict, Severity

SEV_ORDER = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}


@dataclass
class AuditReport:
    verdicts: list[InvoiceVerdict] = field(default_factory=list)

    @property
    def cleared(self) -> list[InvoiceVerdict]:
        return [v for v in self.verdicts if v.clean]

    @property
    def exceptions(self) -> list[InvoiceVerdict]:
        out = [v for v in self.verdicts if not v.clean]
        return sorted(
            out,
            key=lambda v: (
                SEV_ORDER[v.worst_severity],
                -sum(f.dollar_impact_cents for f in v.flags),
            ),
        )

    @property
    def leakage_cents(self) -> int:
        return sum(
            f.dollar_impact_cents
            for v in self.verdicts for f in v.flags
            if f.impact_kind == ImpactKind.LEAKAGE
        )

    @property
    def at_risk_cents(self) -> int:
        # At-risk counts once per invoice (the payment itself), not per flag.
        total = 0
        for v in self.verdicts:
            risk = [f for f in v.flags if f.impact_kind == ImpactKind.AT_RISK]
            if risk:
                total += max(f.dollar_impact_cents for f in risk)
        return total


def render_markdown(report: AuditReport, dossiers: dict[str, str] | None = None) -> str:
    dossiers = dossiers or {}
    lines: list[str] = []
    n = len(report.verdicts)
    lines.append("# Stowaway audit report\n")
    lines.append(
        f"**{n} invoices audited — {len(report.cleared)} cleared to billing, "
        f"{len(report.exceptions)} exceptions.**\n"
    )
    lines.append(
        f"- Recoverable overbilling (leakage): **${report.leakage_cents / 100:,.2f}**\n"
        f"- Payments held pending review (at-risk): **${report.at_risk_cents / 100:,.2f}**\n"
    )
    lines.append("\n## Exceptions, ranked\n")
    for v in report.exceptions:
        inv: Invoice = v.invoice
        impact = sum(f.dollar_impact_cents for f in v.flags)
        lines.append(
            f"\n### {v.worst_severity.value.upper()} · {inv.invoice_id} · "
            f"{inv.carrier_name} (MC {inv.carrier_mc}) · ${impact / 100:,.2f}\n"
        )
        for f in v.flags:
            lines.append(f"- **{f.rule}** ({f.confidence:.0%} conf): {f.summary}")
            for ev in f.evidence:
                cite = f" — [{ev.citation}]" if ev.citation else ""
                lines.append(f"    - {ev.kind}: {ev.detail}{cite}")
        if inv.carrier_mc in dossiers:
            lines.append(f"\n<details><summary>Vendor risk dossier (Tavily /research)</summary>\n")
            lines.append(dossiers[inv.carrier_mc])
            lines.append("\n</details>")
    lines.append("\n## Cleared\n")
    cleared_ids = ", ".join(v.invoice.invoice_id for v in report.cleared) or "none"
    lines.append(cleared_ids + "\n")
    lines.append("\n---\n*Stowaway flags the money. It never moves it.*\n")
    return "\n".join(lines)


def render_chat_ping(report: AuditReport) -> str:
    """The Telegram/Slack message OpenClaw sends after a heartbeat audit.
    Short on purpose: a human reads this on a phone at 4:45 on a Friday."""
    exc = report.exceptions
    if not exc:
        return (
            f"⚓ Stowaway: {len(report.verdicts)} invoices audited, all clear. "
            f"Nothing needs you. Go home."
        )
    top = exc[0]
    top_flag = sorted(top.flags, key=lambda f: -f.dollar_impact_cents)[0]
    return (
        f"⚓ Stowaway: {len(report.verdicts)} invoices audited — "
        f"{len(report.cleared)} cleared, {len(exc)} need eyes.\n"
        f"💸 ${report.leakage_cents / 100:,.0f} recoverable, "
        f"${report.at_risk_cents / 100:,.0f} held.\n"
        f"Worst: {top.invoice.carrier_name} ({top.invoice.invoice_id}) — {top_flag.summary}\n"
        f"Full report with evidence attached. Reply 'release <id>' or 'dispute <id>'."
    )
