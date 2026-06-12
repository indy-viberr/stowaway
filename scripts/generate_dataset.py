"""Generate the synthetic demo dataset + replay fixtures.

Deterministic (seed 1979 — the year the boat was built). Produces:
  data/loads.json, data/invoices.json, data/pods.json, data/answer_key.json
  fixtures/fmcsa.json, fixtures/doe_diesel.json, fixtures/dossiers.json

Everything here is synthetic. No real carriers, customers, or contracts.
Run from repo root:  python3 scripts/generate_dataset.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stowaway.truth import FSC_SCHEDULE, fsc_pct_for_price, week_monday  # noqa: E402

rng = random.Random(1979)

DATA = ROOT / "data"
FIXTURES = ROOT / "fixtures"
DATA.mkdir(exist_ok=True)
FIXTURES.mkdir(exist_ok=True)

# ---------------------------------------------------------------- DOE diesel
# Mondays, April–June 2026. April prices high; recent weeks lower — so a
# carrier quietly re-using April's price overbills by a full FSC bracket.
DOE_WEEKS = {
    "2026-04-13": 4.07,
    "2026-04-20": 4.11,
    "2026-04-27": 3.96,
    "2026-05-04": 3.81,
    "2026-05-11": 3.72,
    "2026-05-18": 3.66,
    "2026-05-25": 3.58,
    "2026-06-01": 3.55,
    "2026-06-08": 3.61,
}

# ---------------------------------------------------------------- carriers
CLEAN_CARRIERS = [
    ("412887", "Meridian Haulage Inc"),
    ("523901", "Bay & Border Freight LLC"),
    ("611234", "Cascade Carriers Corp"),
    ("634710", "Pelican Transport LLC"),
    ("655402", "Ironwood Trucking Co"),
    ("688191", "Sundial Logistics Inc"),
    ("702553", "Comet Line Freight LLC"),
    ("719008", "Harbor Mile Carriers Inc"),
    ("733415", "Prairie Sky Transport LLC"),
    ("748266", "Bluegrass Motor Freight Inc"),
    ("761930", "Sierra Crest Trucking LLC"),
    ("774512", "Lakeshore Freightways Inc"),
    ("789344", "Copperline Carriers LLC"),
    ("801276", "Northstar Drayage Co"),
    ("815648", "Gulf Current Logistics LLC"),
]
PHANTOM_MC = ("998877", "Bluewater Logistics LLC")        # no FMCSA record at all
REVOKED_MC = ("884210", "Redline Carriers Inc")           # authority revoked Jan 2026
MISMATCH_MC = ("771455", "Apex Freight Solutions")        # MC really belongs to Garza Trucking
MISMATCH_LEGAL = "Garza Trucking LLC"

LANES = [
    ("Laredo, TX", "Memphis, TN"), ("Oakland, CA", "Reno, NV"),
    ("El Paso, TX", "Phoenix, AZ"), ("Stockton, CA", "Portland, OR"),
    ("Nuevo Laredo, MX", "San Antonio, TX"), ("Fresno, CA", "Salt Lake City, UT"),
    ("Long Beach, CA", "Las Vegas, NV"), ("Otay Mesa, CA", "Tucson, AZ"),
]
CONSIGNEES = [
    "Westgate Distribution Center", "Hilltop Foods DC #4", "Marquez Produce Co",
    "Summit Building Supply", "Cordova Cold Storage", "Reliant Auto Parts Whse",
    "Pacific Crest Retail DC", "Bluebonnet Beverage Co",
]

# ---------------------------------------------------------------- loads
loads: list[dict] = []
pickup_pool = [d for d in (
    [f"2026-05-{day:02d}" for day in range(18, 30)] + [f"2026-06-{day:02d}" for day in range(1, 6)]
)]
for i in range(55):
    mc, name = rng.choice(CLEAN_CARRIERS)
    o, d = rng.choice(LANES)
    allowed = []
    if rng.random() < 0.5:
        allowed.append({"code": "DET", "max_cents": 40000})
    if rng.random() < 0.35:
        allowed.append({"code": "LUMPER", "max_cents": 15000})
    loads.append({
        "load_id": f"L-{1001 + i}",
        "lane": f"{o} -> {d}",
        "pickup_date": rng.choice(pickup_pool),
        "carrier_mc": mc,
        "carrier_name": name,
        "agreed_linehaul_cents": rng.randrange(120000, 480000, 2500),
        "consignee": rng.choice(CONSIGNEES),
        "accessorials_allowed": allowed,
    })
loads_by_id = {l["load_id"]: l for l in loads}


def correct_fsc(load: dict) -> int:
    price = DOE_WEEKS[week_monday(load["pickup_date"])]
    return round(load["agreed_linehaul_cents"] * fsc_pct_for_price(price))


def stale_fsc(load: dict, stale_week: str = "2026-04-20") -> int:
    return round(load["agreed_linehaul_cents"] * fsc_pct_for_price(DOE_WEEKS[stale_week]))


# ---------------------------------------------------------------- invoices
invoices: list[dict] = []
answer_key: dict[str, list[str]] = {}
inv_n = 0


def add_invoice(load: dict, lines: list[dict], expected: list[str],
                mc: str | None = None, name: str | None = None,
                invoice_date: str | None = None, load_id: str | None = None) -> str:
    global inv_n
    inv_n += 1
    iid = f"INV-{26000 + inv_n}"
    invoices.append({
        "invoice_id": iid,
        "invoice_date": invoice_date or "2026-06-09",
        "carrier_mc": mc or load["carrier_mc"],
        "carrier_name": name or load["carrier_name"],
        "load_id": load_id or load["load_id"],
        "lines": lines,
    })
    if expected:
        answer_key[iid] = sorted(expected)
    return iid


def base_lines(load: dict, fsc: int | None = None) -> list[dict]:
    return [
        {"code": "LINEHAUL", "description": f"Linehaul {load['lane']}", "amount_cents": load["agreed_linehaul_cents"]},
        {"code": "FSC", "description": "Fuel surcharge", "amount_cents": fsc if fsc is not None else correct_fsc(load)},
    ]


# 35 clean invoices on the first 35 loads
for load in loads[:35]:
    lines = base_lines(load)
    if load["accessorials_allowed"] and rng.random() < 0.4:
        a = load["accessorials_allowed"][0]
        lines.append({"code": a["code"], "description": f"{a['code']} per rate con",
                      "amount_cents": rng.randrange(7500, min(a["max_cents"], 30000), 2500)})
    add_invoice(load, lines, expected=[])

# --- planted fraud, one scenario per remaining load ------------------------
L = loads[35:]

# 1) phantom carrier — MC doesn't exist
add_invoice(L[0], base_lines(L[0]), ["PHANTOM_CARRIER"], mc=PHANTOM_MC[0], name=PHANTOM_MC[1])
# matching loads must reference the bad carriers so the story is coherent
L[0]["carrier_mc"], L[0]["carrier_name"] = PHANTOM_MC

# 2) revoked authority
add_invoice(L[1], base_lines(L[1]), ["AUTHORITY_REVOKED"], mc=REVOKED_MC[0], name=REVOKED_MC[1])
L[1]["carrier_mc"], L[1]["carrier_name"] = REVOKED_MC

# 3) double-brokering: name mismatch + they also padded the fuel week (2 flags -> dossier)
add_invoice(L[2], base_lines(L[2], fsc=stale_fsc(L[2])),
            ["CARRIER_NAME_MISMATCH", "STALE_FUEL_WEEK"], mc=MISMATCH_MC[0], name=MISMATCH_MC[1])
L[2]["carrier_mc"], L[2]["carrier_name"] = MISMATCH_MC

# 4-6) stale fuel week x3
for load in L[3:6]:
    add_invoice(load, base_lines(load, fsc=stale_fsc(load)), ["STALE_FUEL_WEEK"])

# 7) duplicate billing: bill load L[6] twice
dup_load = L[6]
add_invoice(dup_load, base_lines(dup_load), [], invoice_date="2026-06-05")
add_invoice(dup_load, base_lines(dup_load), ["DUPLICATE_BILLING"], invoice_date="2026-06-09")

# 8) unauthorized accessorial: LIFTGATE never allowed
load = L[7]
add_invoice(load, base_lines(load) + [
    {"code": "LIFTGATE", "description": "Liftgate service", "amount_cents": 15000}],
    ["UNAUTHORIZED_ACCESSORIAL"])

# 9) unauthorized DET on a load with no DET allowance
load = L[8]
load["accessorials_allowed"] = []
add_invoice(load, base_lines(load) + [
    {"code": "DET", "description": "Detention 3 hrs", "amount_cents": 45000}],
    ["UNAUTHORIZED_ACCESSORIAL"])

# 10) duplicate accessorial: DET billed twice
load = L[9]
load["accessorials_allowed"] = [{"code": "DET", "max_cents": 40000}]
add_invoice(load, base_lines(load) + [
    {"code": "DET", "description": "Detention 2.5 hrs", "amount_cents": 37500},
    {"code": "DET", "description": "Detention 2.5 hrs", "amount_cents": 37500}],
    ["DUPLICATE_ACCESSORIAL"])

# 11-12) linehaul variance
load = L[10]
lines = base_lines(load)
lines[0]["amount_cents"] += 18000
add_invoice(load, lines, ["LINEHAUL_VARIANCE"])
load = L[11]
lines = base_lines(load)
lines[0]["amount_cents"] += 9500
add_invoice(load, lines, ["LINEHAUL_VARIANCE"])

# 13) POD signature missing
pod_sig_missing = L[12]
add_invoice(pod_sig_missing, base_lines(pod_sig_missing), ["POD_SIGNATURE_MISSING"])

# 14) POD missing entirely
pod_missing = L[13]
add_invoice(pod_missing, base_lines(pod_missing), ["POD_MISSING"])

# 15) consignee mismatch (wrong doc attached to the load)
consignee_mismatch = L[14]
add_invoice(consignee_mismatch, base_lines(consignee_mismatch), ["CONSIGNEE_MISMATCH"])

# ---------------------------------------------------------------- PODs
pods: list[dict] = []
billed_load_ids = {inv["load_id"] for inv in invoices}
for lid in sorted(billed_load_ids):
    load = loads_by_id[lid]
    if lid == pod_missing["load_id"]:
        pods.append({"load_id": lid, "present": False})
        continue
    rec = {
        "load_id": lid,
        "present": True,
        "signature_present": True,
        "signature_legibility": round(rng.uniform(0.62, 0.97), 2),
        "date_legible": True,
        "consignee_name": load["consignee"],
        "doc_quality": round(rng.uniform(0.55, 0.95), 2),
    }
    if lid == pod_sig_missing["load_id"]:
        rec["signature_present"] = False
        rec["signature_legibility"] = 0.0
    if lid == consignee_mismatch["load_id"]:
        rec["consignee_name"] = "Eastline Paper Products"   # wrong site entirely
    pods.append(rec)

# ---------------------------------------------------------------- fixtures
fmcsa: dict[str, dict] = {}
for mc, name in CLEAN_CARRIERS:
    fmcsa[mc] = {"found": True, "legal_name": name, "authority": "ACTIVE",
                 "source": f"synthetic:fmcsa-safer/MC-{mc}"}
fmcsa[PHANTOM_MC[0]] = {"found": False, "source": f"synthetic:fmcsa-safer/MC-{PHANTOM_MC[0]}"}
fmcsa[REVOKED_MC[0]] = {"found": True, "legal_name": REVOKED_MC[1], "authority": "REVOKED",
                        "source": f"synthetic:fmcsa-safer/MC-{REVOKED_MC[0]}"}
fmcsa[MISMATCH_MC[0]] = {"found": True, "legal_name": MISMATCH_LEGAL, "authority": "ACTIVE",
                         "source": f"synthetic:fmcsa-safer/MC-{MISMATCH_MC[0]}"}

dossiers = {
    MISMATCH_MC[0]: {"report_md": (
        "**Vendor risk dossier — 'Apex Freight Solutions' (MC 771455)** *(synthetic demo fixture; "
        "live mode generates this via Tavily /research with real citations)*\n\n"
        "- MC 771455 is registered to **Garza Trucking LLC** (El Paso, TX), not 'Apex Freight Solutions'. "
        "[synthetic:fmcsa-safer/MC-771455]\n"
        "- 'Apex Freight Solutions LLC' was registered **11 weeks ago**; registered agent address "
        "resolves to a mailbox store in Doral, FL. [synthetic:sunbiz/apex-freight]\n"
        "- Remit-to bank account changed once already this quarter. [synthetic:internal/remit-history]\n"
        "- Pattern match: consistent with **double-brokering** — a shell invoicing under a real "
        "carrier's MC. Recommended action: hold payment, verify with Garza Trucking dispatch directly.\n"
    )},
}

# ---------------------------------------------------------------- write
(DATA / "loads.json").write_text(json.dumps(loads, indent=2))
(DATA / "invoices.json").write_text(json.dumps(invoices, indent=2))
(DATA / "pods.json").write_text(json.dumps(pods, indent=2))
(DATA / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True))
(FIXTURES / "fmcsa.json").write_text(json.dumps(fmcsa, indent=2, sort_keys=True))
(FIXTURES / "doe_diesel.json").write_text(json.dumps(
    {k: {"price": v} for k, v in DOE_WEEKS.items()}, indent=2, sort_keys=True))
(FIXTURES / "dossiers.json").write_text(json.dumps(dossiers, indent=2, sort_keys=True))

print(f"wrote {len(loads)} loads, {len(invoices)} invoices, {len(pods)} PODs, "
      f"{len(answer_key)} planted-fraud invoices (see data/answer_key.json)")
