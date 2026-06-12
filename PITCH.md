# The 90-second pitch — boat day

*Ninety seconds, delivered on the water. Specificity beats slogans. Timings assume a measured pace; practice at 80 seconds so nerves have room.*

---

**[0:00 — the scene]**
It's 4:45 on a Friday at a 300-truck freight brokerage. The AP clerk has 200 carrier invoices in her queue. Every check is trivial. Does this carrier's MC number exist. Was this fuel surcharge computed from this week's diesel price. Didn't we already pay this load. At volume, trivial checks get skipped — and skipped checks always favor the carrier.

**[0:20 — the villain]**
One of today's invoices is from a company that does not exist. Double-brokering fraud — shells invoicing under real carriers' MC numbers — costs this industry about eight hundred million dollars a year. The clerk is supposed to catch it by hand. On Friday. At 4:45.

**[0:35 — the insight]**
Here's the thing every AP tool misses: half the truth an invoice must match lives *outside* your company, and it changes weekly. Your system knows what you agreed to pay. It does not know whether MC 998877 exists, or what diesel cost on Monday. Every other agent searches the web to write something. Stowaway searches the web to call bullshit.

**[0:50 — the demo beat]**
*(turn the laptop / play the clip)* This is a live Telegram thread. Stowaway audited 51 invoices while we were at lunch: 36 cleared, 15 flagged, every flag with receipts — the phantom carrier with the FMCSA citation, the fuel surcharge computed off April's diesel price, the duplicate. $4,751 recoverable, $24,846 held. It found every fraud in the dataset and falsely accused no one — that's a committed test, not a claim.

**[1:10 — the stack, fast]**
OpenClaw is the runtime — heartbeat wakes it, it lives in chat. Tavily is the truth layer — FMCSA, the DOE index, cited research dossiers. Composio reads the inbox and routes the exceptions. Every token of inference is an open model on Nebius. And one thing we didn't have to guess about: we run our own company's AP ops on OpenClaw, in production. This is the primitive we trust most, rebuilt in the open.

**[1:25 — the close]**
Stowaway flags the money. It never moves it. The clerk reviews fifteen exceptions instead of two hundred invoices — and goes home at five. *(beat)* Freight audit firms charge a percentage of recovery for this. We do it before the money leaves.

---

## Likely Q&A (investors + sponsors)

**"What would you charge?"** — Audit-and-pay firms charge 2–5% of recovered dollars, post-payment. Pre-payment interception is worth more and costs less to deliver: per-invoice SaaS, $2–5K/month mid-market, which is what this segment already pays for tools that do less.

**"Why won't the carrier just adapt?"** — The checks are against external records the carrier doesn't control: FMCSA, the DOE index, state registries. Adapting means committing fraud in a different database.

**"What's defensible here?"** — The validation engine is generic; the moat is the encoded tribal knowledge per customer — tolerance bands, accessorial deals, which exceptions are routine. Each deployment makes the next one faster. (Don't say more than this.)

**"Hallucinations in the money math?"** — There's no LLM in the money math. Dollars are computed by tested deterministic code; models only read scans and summarize research, always with confidence scores, always routed to a human. The agent cannot release a payment. Architecturally cannot, not policy cannot.

**"Why didn't you use [closed frontier model]?"** — Didn't need it. Open models on Token Factory read the PODs and write the dossiers; the hard guarantees come from code, not model IQ. (This answer is also Nebius's favorite sentence.)

**"What breaks at scale?"** — Per-contract FSC schedules, SAFER parsing robustness, and rate-confirmation ingestion across formats. We know because we hit these in production at our own company — they're engineering, not research.

## Delivery notes
- The Telegram screenshot is the pitch. Everything else is setup for it.
- Say "$4,751" and "fifteen exceptions instead of two hundred invoices" exactly — concrete numbers are what survive in listeners' notes.
- If the kayak race happened before presentations: one line of brine-flavored joke max, then back to the clerk.
