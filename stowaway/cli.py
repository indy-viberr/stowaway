"""Stowaway CLI — the full three-phase loop.

    python3 -m stowaway.cli audit --replay     # zero keys, fixtures only
    python3 -m stowaway.cli audit --live       # real Tavily / Token Factory

OpenClaw runs this same entrypoint from its heartbeat (see skill/SKILL.md).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import intake, matcher, reconcile
from .models import InvoiceVerdict
from .replay import FixtureStore
from .truth import TruthClient

ROOT = Path(__file__).resolve().parent.parent


def audit(mode: str, data_dir: Path, out_path: Path) -> reconcile.AuditReport:
    t0 = time.time()
    print(f"⚓ Stowaway audit · mode={mode}")

    # ---- Phase 1: INTAKE ----------------------------------------------------
    loads, invoices, pods = intake.load_dataset(data_dir)
    print(f"  intake        {len(invoices)} invoices · {len(loads)} loads · {len(pods)} PODs")

    # ---- Phase 2: VALIDATION ------------------------------------------------
    truth = TruthClient(FixtureStore(ROOT / "fixtures"), mode=mode)
    verdicts: list[InvoiceVerdict] = []
    for inv in invoices:
        flags = []
        flags += matcher.match_invoice(inv, loads, pods)           # internal truth
        flags += truth.check_carrier(inv)                          # external: FMCSA
        load = loads.get(inv.load_id)
        if load is not None:
            flags += truth.check_fuel_surcharge(inv, load)         # external: DOE
        verdicts.append(InvoiceVerdict(invoice=inv, flags=flags))
    # cross-invoice checks
    dup_flags = matcher.find_duplicate_billing(invoices)
    by_inv = {v.invoice.invoice_id: v for v in verdicts}
    for f in dup_flags:
        by_inv[f.invoice_id].flags.append(f)
    n_flags = sum(len(v.flags) for v in verdicts)
    print(f"  validation    {n_flags} flags across {sum(1 for v in verdicts if v.flags)} invoices")

    # escalation: dossier for any vendor tripping >= 2 flags
    dossiers: dict[str, str] = {}
    for v in verdicts:
        if len(v.flags) >= 2 and v.invoice.carrier_mc not in dossiers:
            try:
                dossiers[v.invoice.carrier_mc] = truth.vendor_dossier(v.invoice)
            except Exception as e:  # noqa: BLE001 — degrade gracefully, visibly
                print(f"  dossier       skipped for MC {v.invoice.carrier_mc}: {e}", file=sys.stderr)
    if dossiers:
        print(f"  dossiers      {len(dossiers)} vendor deep-dives (Tavily /research)")

    # ---- Phase 3: RECONCILIATION ---------------------------------------------
    report = reconcile.AuditReport(verdicts=verdicts)
    out_path.write_text(reconcile.render_markdown(report, dossiers))
    print(f"  reconcile     {len(report.cleared)} cleared · {len(report.exceptions)} exceptions")
    print(f"  report        {out_path}")
    print()
    print(reconcile.render_chat_ping(report))
    print(f"\n  done in {time.time() - t0:.2f}s")
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="stowaway")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="run the three-phase audit loop")
    g = a.add_mutually_exclusive_group()
    g.add_argument("--replay", action="store_true", help="fixtures only, no keys (default)")
    g.add_argument("--live", action="store_true", help="real Tavily / Token Factory")
    a.add_argument("--data", default=str(ROOT / "data"), help="dataset directory")
    a.add_argument("--out", default=str(ROOT / "report.md"), help="report output path")
    args = p.parse_args(argv)

    mode = "live" if args.live else "replay"
    audit(mode, Path(args.data), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
