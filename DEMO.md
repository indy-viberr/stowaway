# Demo video — 90-second storyboard

*Format: screen recording, phone-vertical crop for socials, landscape master for the submission. The chat app is the star; the terminal is the proof; the POD scan is the surprise.*

| Time | Shot | On screen | Voiceover / caption |
|---|---|---|---|
| 0:00–0:08 | Telegram thread, quiet | Yesterday's message: *"⚓ 48 invoices audited, all clear. Nothing needs you. Go home."* | "This is our freight auditor. Most days it says one thing." |
| 0:08–0:18 | New ping arrives (live) | *"⚓ 51 invoices audited — 36 cleared, 15 need eyes. 💸 $4,751 recoverable, $24,846 held. Worst: Bluewater Logistics — MC 998877 does not exist in FMCSA records. Do not pay."* | "Today is not most days." |
| 0:18–0:32 | User types: *"why is INV-26038 flagged"* — agent replies with the evidence chain | The double-brokering flag: invoice name vs FMCSA legal name, citation links | "It doesn't just flag. It shows receipts — government records, fetched live." |
| 0:32–0:44 | The fuel catch, zoomed | *"Billed FSC matches the week of April 13 — a stale, higher price. This week's DOE diesel: $3.66."* | "It knows what diesel cost on Monday. The carrier hoped you didn't." |
| 0:44–0:56 | Split: POD scan image (data/pod_scans) next to the flag | A signed delivery receipt; then one with an empty signature box, flagged | "It reads the paper, too. Vision model, open weights, on Nebius." |
| 0:56–1:08 | Terminal: `make demo` runs; tests pass | `36 cleared · 15 exceptions · done in 0.04s` and `Ran 26 tests OK` | "Every fraud in the test set found. Zero false accusations. That's a committed test, not a promise." |
| 1:08–1:20 | Architecture diagram (ARCHITECTURE.md mermaid render) | Three phases: intake → validation → reconciliation | "Tavily for truth. Composio for the inbox. OpenClaw for the loop. Nebius for every token." |
| 1:20–1:30 | Back to Telegram: user types *"release INV-26041"*, agent logs it | Decision logged; agent confirms | "It flags the money. It never moves it. Humans keep the keys." |

## Production notes
- Record the Telegram interactions for real (OpenClaw gateway running) — the OpenClaw community can smell a mocked chat UI.
- The "all clear, go home" beat is the most relatable two seconds for ops people; do not cut it.
- Keep one continuous take of `make demo` — no edits mid-run; people replay these frame-by-frame.
- End card: ⚓ **Stowaway — finds the charges hiding in your hull.** Repo URL + the five sponsor tags.
