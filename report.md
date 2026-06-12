# Stowaway audit report

**51 invoices audited — 36 cleared to billing, 15 exceptions.**

- Recoverable overbilling (leakage): **$4,751.00**
- Payments held pending review (at-risk): **$24,846.00**


## Exceptions, ranked


### CRITICAL · INV-26036 · Bluewater Logistics LLC (MC 998877) · $5,520.00

- **PHANTOM_CARRIER** (97% conf): MC 998877 does not exist in FMCSA records. Do not pay.
    - web: FMCSA SAFER: no record for MC 998877 — [synthetic:fmcsa-safer/MC-998877]

### CRITICAL · INV-26038 · Apex Freight Solutions (MC 771455) · $4,992.00

- **CARRIER_NAME_MISMATCH** (85% conf): Invoice says 'Apex Freight Solutions' but MC 771455 belongs to 'Garza Trucking LLC'. Classic double-brokering signature.
    - field: invoice carrier_name: Apex Freight Solutions
    - web: FMCSA legal name for MC 771455: Garza Trucking LLC — [synthetic:fmcsa-safer/MC-771455]
- **STALE_FUEL_WEEK** (90% conf): Fuel surcharge overbilled by $156.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.
    - web: DOE on-highway diesel, week of 2026-05-18: $3.660/gal — [fixture:doe_diesel[2026-05-18]]
    - computation: expected FSC = $3,900.00 x 20% = $780.00; billed $936.00
    - computation: billed FSC reverse-matches DOE week 2026-04-13

<details><summary>Vendor risk dossier (Tavily /research)</summary>

**Vendor risk dossier — 'Apex Freight Solutions' (MC 771455)** *(synthetic demo fixture; live mode generates this via Tavily /research with real citations)*

- MC 771455 is registered to **Garza Trucking LLC** (El Paso, TX), not 'Apex Freight Solutions'. [synthetic:fmcsa-safer/MC-771455]
- 'Apex Freight Solutions LLC' was registered **11 weeks ago**; registered agent address resolves to a mailbox store in Doral, FL. [synthetic:sunbiz/apex-freight]
- Remit-to bank account changed once already this quarter. [synthetic:internal/remit-history]
- Pattern match: consistent with **double-brokering** — a shell invoicing under a real carrier's MC. Recommended action: hold payment, verify with Garza Trucking dispatch directly.


</details>

### CRITICAL · INV-26037 · Redline Carriers Inc (MC 884210) · $4,410.00

- **AUTHORITY_REVOKED** (95% conf): MC 884210 authority is REVOKED — carrier was not authorized to haul this load.
    - web: FMCSA authority status: REVOKED — [synthetic:fmcsa-safer/MC-884210]

### CRITICAL · INV-26043 · Sundial Logistics Inc (MC 688191) · $3,030.00

- **DUPLICATE_BILLING** (100% conf): Load L-1042 already billed on invoice INV-26042 (2026-06-05); INV-26043 is a duplicate.
    - field: 2 invoices reference load L-1042: INV-26042, INV-26043

### HIGH · INV-26051 · Meridian Haulage Inc (MC 412887) · $4,020.00

- **CONSIGNEE_MISMATCH** (85% conf): POD signed at 'Eastline Paper Products' but load consignee is 'Summit Building Supply'. Possibly the wrong document attached.
    - pod: POD consignee: Eastline Paper Products
    - field: TMS consignee: Summit Building Supply

### HIGH · INV-26050 · Bay & Border Freight LLC (MC 523901) · $3,750.00

- **POD_MISSING** (100% conf): No proof-of-delivery on file. Invoice cannot clear to billing.
    - pod: no POD document matched to this load

### HIGH · INV-26049 · Copperline Carriers LLC (MC 789344) · $2,310.00

- **POD_SIGNATURE_MISSING** (95% conf): POD scan has no receiver signature.
    - pod: vision model: signature_present=false

### MEDIUM · INV-26045 · Lakeshore Freightways Inc (MC 774512) · $450.00

- **UNAUTHORIZED_ACCESSORIAL** (100% conf): Accessorial 'DET' (Detention 3 hrs) not in agreed schedule for this load.
    - field: allowed accessorials: none; billed: DET $450.00

### MEDIUM · INV-26046 · Gulf Current Logistics LLC (MC 815648) · $375.00

- **DUPLICATE_ACCESSORIAL** (100% conf): Accessorial 'DET' appears 2x on one invoice.
    - field: 2 lines with code=DET

### MEDIUM · INV-26047 · Sundial Logistics Inc (MC 688191) · $180.00

- **LINEHAUL_VARIANCE** (100% conf): Linehaul billed $2,930.00 vs agreed $2,750.00 (tolerance $27.50).
    - field: rate confirmation: agreed_linehaul=$2,750.00
    - computation: delta=$180.00 > tolerance=$27.50

### MEDIUM · INV-26040 · Gulf Current Logistics LLC (MC 815648) · $159.00

- **STALE_FUEL_WEEK** (90% conf): Fuel surcharge overbilled by $159.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.
    - web: DOE on-highway diesel, week of 2026-06-01: $3.550/gal — [fixture:doe_diesel[2026-06-01]]
    - computation: expected FSC = $3,975.00 x 20% = $795.00; billed $954.00
    - computation: billed FSC reverse-matches DOE week 2026-04-13

### MEDIUM · INV-26044 · Comet Line Freight LLC (MC 702553) · $150.00

- **UNAUTHORIZED_ACCESSORIAL** (100% conf): Accessorial 'LIFTGATE' (Liftgate service) not in agreed schedule for this load.
    - field: allowed accessorials: ['LUMPER']; billed: LIFTGATE $150.00

### MEDIUM · INV-26041 · Prairie Sky Transport LLC (MC 733415) · $95.00

- **STALE_FUEL_WEEK** (90% conf): Fuel surcharge overbilled by $95.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.
    - web: DOE on-highway diesel, week of 2026-05-18: $3.660/gal — [fixture:doe_diesel[2026-05-18]]
    - computation: expected FSC = $2,375.00 x 20% = $475.00; billed $570.00
    - computation: billed FSC reverse-matches DOE week 2026-04-13

### MEDIUM · INV-26048 · Sundial Logistics Inc (MC 688191) · $95.00

- **LINEHAUL_VARIANCE** (100% conf): Linehaul billed $3,770.00 vs agreed $3,675.00 (tolerance $36.75).
    - field: rate confirmation: agreed_linehaul=$3,675.00
    - computation: delta=$95.00 > tolerance=$36.75

### MEDIUM · INV-26039 · Bluegrass Motor Freight Inc (MC 748266) · $61.00

- **STALE_FUEL_WEEK** (90% conf): Fuel surcharge overbilled by $61.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.
    - web: DOE on-highway diesel, week of 2026-05-18: $3.660/gal — [fixture:doe_diesel[2026-05-18]]
    - computation: expected FSC = $1,525.00 x 20% = $305.00; billed $366.00
    - computation: billed FSC reverse-matches DOE week 2026-04-13

## Cleared

INV-26001, INV-26002, INV-26003, INV-26004, INV-26005, INV-26006, INV-26007, INV-26008, INV-26009, INV-26010, INV-26011, INV-26012, INV-26013, INV-26014, INV-26015, INV-26016, INV-26017, INV-26018, INV-26019, INV-26020, INV-26021, INV-26022, INV-26023, INV-26024, INV-26025, INV-26026, INV-26027, INV-26028, INV-26029, INV-26030, INV-26031, INV-26032, INV-26033, INV-26034, INV-26035, INV-26042


---
*Stowaway flags the money. It never moves it.*
