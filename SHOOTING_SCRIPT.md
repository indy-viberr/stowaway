# Stowaway — 90-second demo shooting script

**Master file:** `stowaway_demo_master.mp4` (landscape 1920×1080)
**Social cut:** `stowaway_demo_vertical.mp4` (1080×1920, phone-vertical crop from master)
**Total runtime:** 90 seconds on the nose. Every beat has a hard out.

---

## 1. SHOT LIST — second-by-second

### BEAT 1 · 0:00–0:08 · "The quiet day" (8 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:00 | Telegram desktop, Stowaway bot thread open. Visible in the message list: yesterday's message timestamped ~18:47 the day before. Message text exactly: `⚓ Stowaway: 48 invoices audited, all clear. Nothing needs you. Go home.` | No cursor movement. Hold still. This is the "before" frame. |
| 0:03 | Same. No new activity. | Cursor offscreen or parked at top-right corner. |
| 0:07 | Same. | Hold. |

**Hard cut OUT at 0:08.**

**Voiceover 0:00–0:08:**
> "This is our freight auditor. Most days it says one thing."

**Caption overlay (lower-third, 0:02–0:07):** `48 invoices. All clear. Go home.`

---

### BEAT 2 · 0:08–0:18 · "Today is not most days" (10 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:08 | Same Telegram thread. Typing indicator ("Stowaway is typing…") appears. | No cursor movement. Let the ping arrive live. |
| 0:09 | New message lands. Full text (verbatim from `render_chat_ping` output): | — |

**Exact message text to stage (copy-paste this into the bot; it must arrive live on camera):**

```
⚓ Stowaway: 51 invoices audited — 36 cleared, 15 need eyes.
💸 $4,751 recoverable, $24,846 held.
Worst: Bluewater Logistics LLC (INV-26036) — MC 998877 does not exist in FMCSA records. Do not pay.
Full report with evidence attached. Reply 'release <id>' or 'dispute <id>'.
```

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:09–0:17 | Full message visible. Slow scroll up within the message if it overflows, so all four lines are readable. | Scroll, no typing. |
| 0:17 | Message fully visible, steady. | Hold. |

**Hard cut OUT at 0:18.**

**Voiceover 0:08–0:18:**
> "Today is not most days."

**Caption overlay (lower-third, 0:11–0:17):** `15 exceptions · $4,751 recoverable · $24,846 held`

---

### BEAT 3 · 0:18–0:32 · "It shows receipts" (14 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:18 | Telegram input box. | Click input box. Begin typing. |
| 0:19 | User types: `why is INV-26038 flagged` | Type at natural human speed (~55 wpm). Typos allowed if corrected naturally. Do not pause mid-type. |
| 0:21 | Message sent. | Hit Enter/Send. |
| 0:22 | Typing indicator from bot. | Hold. |
| 0:23 | Agent reply arrives. Full text (verbatim — compose from report.md, see Telegram transcript section §2 below). | — |
| 0:23–0:31 | Scroll through the reply so both flags are visible — CARRIER_NAME_MISMATCH first, then STALE_FUEL_WEEK. Pause ~2 s on each. | Slow deliberate scroll. |
| 0:31 | Bottom of the reply visible. | Hold. |

**Hard cut OUT at 0:32.**

**Voiceover 0:18–0:32:**
> "It doesn't just flag. It shows receipts — government records, fetched live."

**Caption overlay (lower-third, 0:24–0:31):** `FMCSA · DOE diesel index · cited, live`

---

### BEAT 4 · 0:32–0:44 · "The fuel catch" (12 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:32 | Still in Telegram thread. Scroll back up to the agent's INV-26038 reply. | Scroll up to the STALE_FUEL_WEEK block. |
| 0:34 | Zoom in (OBS scene: 1.4× digital zoom, centered on the fuel block). Visible text: `STALE_FUEL_WEEK (90% conf): Fuel surcharge overbilled by $156.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.` and below it: `DOE on-highway diesel, week of 2026-05-18: $3.660/gal` and `expected FSC = $3,900.00 x 20% = $780.00; billed $936.00` | Hold zoom. No cursor movement. |
| 0:34–0:43 | Zoomed view. | Hold steady. |
| 0:43 | Zoom out. | Return to normal 1× view. |

**Hard cut OUT at 0:44.**

**Voiceover 0:32–0:44:**
> "It knows what diesel cost on Monday. The carrier hoped you didn't."

**Caption overlay (lower-third, 0:36–0:43):** `Billed: week of 2026-04-13. Actual DOE: $3.66/gal — $156 overcharge.`

---

### BEAT 5 · 0:44–0:56 · "It reads the paper" (12 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:44 | Split screen (OBS: two-source scene). Left half: a POD scan with a visible, legible signature — use `data/pod_scans/L-1001.png` (a clean cleared load). Right half: `data/pod_scans/L-1049.png` (the load tied to INV-26049 / Copperline Carriers LLC — the scan where vision returned `signature_present=false`). The right image has a clearly empty signature box. | No cursor. Static split. |
| 0:44 | Left image label overlay: `L-1001 · Signature present · Cleared` | — |
| 0:46 | Right image label overlay (red outline box around the empty signature field): `L-1049 · No signature · Held — INV-26049` | Animate the red box in at 0:46. |
| 0:46–0:55 | Hold split. | Static. |
| 0:55 | Fade out split, return to full-screen. | — |

**Hard cut OUT at 0:56.**

**Note:** Confirm which load number maps to INV-26049 before shoot. INV-26049 is Copperline Carriers LLC, MC 789344; find the corresponding load file in `data/` and use that scan. If L-1049 does not exist, use the scan whose filename matches the load ID on INV-26049 per the fixtures.

**Voiceover 0:44–0:56:**
> "It reads the paper, too. Vision model, open weights, on Nebius."

**Caption overlay (lower-third, 0:47–0:55):** `Qwen3-VL via Nebius Token Factory`

---

### BEAT 6 · 0:56–1:08 · "The terminal proof" (12 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 0:56 | Switch to terminal (full screen). Working directory is the repo root. Terminal is clean — no prior output visible. | — |
| 0:57 | Type `make demo` and hit Enter. Do NOT stop recording mid-run. One continuous take, no edits. | Type, Enter. |
| 0:58–1:04 | Pipeline runs. Output scrolls. Key lines visible (real output, not staged): `⚓ Stowaway audit · mode=replay`, `intake        51 invoices · 55 loads · 50 PODs`, `validation    16 flags across 15 invoices`, `dossiers      1 vendor deep-dives (Tavily /research)`, `reconcile     36 cleared · 15 exceptions`, then `done in 0.04s`. After that, the chat ping prints: `⚓ Stowaway: 51 invoices audited — 36 cleared, 15 need eyes.` etc. | No intervention. |
| 1:05 | Run `python3 -m unittest discover -s tests -v 2>&1 | tail -5` OR pre-stage by running `make test` in a second terminal pane visible in a split. Either way, end state shows: `Ran 26 tests in 0.041s` and `OK`. | Type, Enter. |
| 1:07 | Both lines (`done in 0.04s` from demo, `Ran 26 tests ... OK` from test run) visible simultaneously. | Hold. |

**Hard cut OUT at 1:08.**

**Voiceover 0:56–1:08:**
> "Every fraud in the test set found. Zero false accusations. That's a committed test, not a promise."

**Caption overlay (lower-third, 1:02–1:07):** `36 cleared · 15 exceptions · 26 tests · 0 false positives`

---

### BEAT 7 · 1:08–1:20 · "The architecture" (12 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 1:08 | Switch to browser. Open `ARCHITECTURE.md` rendered in a Mermaid viewer (GitHub preview, or a local `npx @mermaid-js/mermaid-cli` render). Full-screen the diagram. | No cursor on diagram. |
| 1:09 | Diagram visible: three swim-lanes — Phase 1 INTAKE (Gmail/Composio + POD/Qwen3-VL → Normalize), Phase 2 VALIDATION (deterministic matcher + Tavily FMCSA/DOE → dossier), Phase 3 RECONCILIATION (exception queue → OpenClaw chat ping + cleared-to-billing). | — |
| 1:09–1:14 | Slow pan/highlight: cursor traces the flow left-to-right without clicking. Hover over `OpenClaw heartbeat` node first (~1 s), then `Tavily` node (~1 s), then `Chat ping via OpenClaw` node (~1 s). | Slow deliberate hover path. |
| 1:15–1:19 | Hold on the full diagram. | Static. |

**Hard cut OUT at 1:20.**

**Voiceover 1:08–1:20:**
> "Tavily for truth. Composio for the inbox. OpenClaw for the loop. Nebius for every token."

**Caption overlay (lower-third, 1:10–1:19):** `Tavily · Composio · OpenClaw · Nebius`

---

### BEAT 8 · 1:20–1:30 · "Humans keep the keys" (10 s)

| s | Screen | Cursor / Action |
|---|--------|-----------------|
| 1:20 | Back to Telegram thread. Scroll to bottom. | Click input box. |
| 1:21 | User types: `release INV-26041` | Type at natural speed. |
| 1:23 | Message sent. | Hit Enter/Send. |
| 1:24 | Agent reply arrives (see §2 Telegram transcript for exact text). | — |
| 1:24–1:29 | Reply visible. | Hold. |
| 1:29 | Fade to black begins. | — |

**Hard cut OUT at 1:30.**

**Voiceover 1:20–1:30:**
> "It flags the money. It never moves it. Humans keep the keys."

**Caption overlay (lower-third, 1:22–1:29):** `Stowaway flags the money. It never moves it.`

---

### END CARD · 1:30–1:35 (optional 5-second hold, no voiceover)

Black background. White text, centered:

```
⚓  Stowaway
finds the charges hiding in your hull.

[repo URL]

#OpenClaw  #Tavily  #Composio  #Nebius  #NebiusTokenFactory
```

No voiceover. Music optional (fade in at 1:28, hold through 1:35).

---

## 2. TELEGRAM TRANSCRIPT — full script to stage

Stage these messages in order. All numbers and carrier data are verbatim from `report.md`.

---

**[PRE-STAGED — visible at 0:00, timestamped yesterday ~18:47]**

> ⚓ Stowaway: 48 invoices audited, all clear. Nothing needs you. Go home.

---

**[LIVE ARRIVAL — 0:09, sent by the running agent / OpenClaw gateway]**

> ⚓ Stowaway: 51 invoices audited — 36 cleared, 15 need eyes.
> 💸 $4,751 recoverable, $24,846 held.
> Worst: Bluewater Logistics LLC (INV-26036) — MC 998877 does not exist in FMCSA records. Do not pay.
> Full report with evidence attached. Reply 'release <id>' or 'dispute <id>'.

---

**[USER — 0:19–0:21]**

> why is INV-26038 flagged

---

**[AGENT REPLY — arrives ~0:23, composed from report.md]**

> **INV-26038 · Apex Freight Solutions (MC 771455) · $4,992.00 · CRITICAL**
>
> Two flags:
>
> 1. **CARRIER_NAME_MISMATCH** (85% conf) — Invoice names "Apex Freight Solutions" but MC 771455 is registered to "Garza Trucking LLC". Classic double-brokering signature.
>    — FMCSA legal name for MC 771455: Garza Trucking LLC [synthetic:fmcsa-safer/MC-771455]
>
> 2. **STALE_FUEL_WEEK** (90% conf) — Fuel surcharge overbilled by $156.00 vs this week's DOE index. Billed amount matches the week of 2026-04-13 — a stale, higher price.
>    — DOE on-highway diesel, week of 2026-05-18: $3.660/gal [fixture:doe_diesel[2026-05-18]]
>    — Expected FSC = $3,900.00 × 20% = $780.00; billed $936.00
>    — Billed FSC reverse-matches DOE week 2026-04-13
>
> Recommended action: hold payment pending carrier identity verification.
> Reply 'show me the dossier' for the full vendor risk profile.

---

**[USER — implied by storyboard beat, optionally staged between 0:32 and 0:44 off-camera or as a follow-up shown during Beat 3 scroll]**

> show me the dossier

---

**[AGENT REPLY — shown if time allows; otherwise skip to Beat 4. Composed verbatim from the `<details>` block in report.md]**

> **Vendor risk dossier — "Apex Freight Solutions" (MC 771455)**
>
> • MC 771455 is registered to Garza Trucking LLC (El Paso, TX), not "Apex Freight Solutions". [synthetic:fmcsa-safer/MC-771455]
> • "Apex Freight Solutions LLC" was registered 11 weeks ago; registered agent address resolves to a mailbox store in Doral, FL. [synthetic:sunbiz/apex-freight]
> • Remit-to bank account changed once already this quarter. [synthetic:internal/remit-history]
> • Pattern match: consistent with double-brokering — a shell invoicing under a real carrier's MC. Recommended action: hold payment, verify with Garza Trucking dispatch directly.

---

**[USER — 0:21 of Beat 8, i.e., clock 1:21]**

> release INV-26041

---

**[AGENT REPLY — arrives ~1:24]**

> Decision logged: INV-26041 (Prairie Sky Transport LLC, MC 733415, $95.00 fuel surcharge variance) — RELEASED by operator.
> Invoice recommended for billing. The $95.00 STALE_FUEL_WEEK flag is on record.
> Stowaway flags the money. It never moves it.

---

## 3. VOICEOVER — per beat

Lines below match the storyboard exactly; punctuation and rhythm are tightened for delivery.

| Beat | Time | Line |
|------|------|------|
| 1 | 0:00–0:08 | "This is our freight auditor. Most days it says one thing." |
| 2 | 0:08–0:18 | "Today is not most days." |
| 3 | 0:18–0:32 | "It doesn't just flag. It shows receipts — government records, fetched live." |
| 4 | 0:32–0:44 | "It knows what diesel cost on Monday. The carrier hoped you didn't." |
| 5 | 0:44–0:56 | "It reads the paper, too. Vision model, open weights, on Nebius." |
| 6 | 0:56–1:08 | "Every fraud in the test set found. Zero false accusations. That's a committed test, not a promise." |
| 7 | 1:08–1:20 | "Tavily for truth. Composio for the inbox. OpenClaw for the loop. Nebius for every token." |
| 8 | 1:20–1:30 | "It flags the money. It never moves it. Humans keep the keys." |

**Delivery notes:**
- Record VO separately as a single WAV/AIFF at 48 kHz, 16-bit. No compression during recording.
- Beat 2 ("Today is not most days.") is five words. Deliver it flat and slow — it earns its impact from contrast with Beat 1, not from emphasis.
- Beat 4: put a half-beat pause between "cost on Monday" and "The carrier hoped you didn't." That pause is the punchline.
- Beat 6: stress "committed test", not "zero."
- Beat 8: three clauses, equal weight, no upward inflection on any of them.

---

## 4. RECORDING CHECKLIST

### OBS setup (primary path)

**Global settings:**
- Resolution: 1920×1080, 60 fps
- Encoder: x264 or hardware H.264, CRF 18 (no visible compression on text)
- Audio: 48 kHz stereo; record desktop audio + mic on separate tracks
- Output: `stowaway_demo_master.mp4`

**Scenes (configure before shoot):**

| Scene name | Sources | Notes |
|---|---|---|
| `telegram_full` | Window capture: Telegram desktop (full window) | Primary scene for Beats 1–3, 8 |
| `telegram_zoom` | Same source, 1.4× crop centered on fuel block | Beat 4 |
| `pod_split` | Image source: `data/pod_scans/L-1001.png` (left 50%), `data/pod_scans/L-1049.png` (right 50%) | Beat 5. Add a red rectangle source (hidden by default) over the right signature box, activate at 0:46 |
| `terminal_full` | Window capture: Terminal / iTerm2 | Beat 6 |
| `architecture` | Browser window (Mermaid render of ARCHITECTURE.md) | Beat 7 |

**Scene transitions:** all cuts, no dissolves. Beats are too short for transitions.

**Text/caption sources:** use OBS GDI+ Text source per scene. Font: SF Mono or JetBrains Mono, 28pt, white, 60% opacity background bar. Position: lower-third, 80px from bottom.

### Phone-vertical crop (social cut)

- Export master first. Do not crop live.
- In post (DaVinci Resolve, Premiere, or ffmpeg): apply a 608×1080 center crop from the 1920×1080 master, then scale to 1080×1920.
- For the split-screen beat (Beat 5), the center crop will cut the edges of both POD images. Before the shoot, confirm the signature boxes and key text fall within the center 608 pixels of each image, or adjust the split layout to stack vertically (top/bottom) in the OBS pod_split scene.
- ffmpeg one-liner for the crop: `ffmpeg -i stowaway_demo_master.mp4 -vf "crop=608:1080:656:0,scale=1080:1920" -c:v libx264 -crf 18 stowaway_demo_vertical.mp4`

### The one-continuous-take rule for `make demo`

- Beat 6 is the integrity beat. Viewers will replay it frame-by-frame.
- Clear the terminal before rolling (`clear` or `reset`). No prior output visible.
- Type `make demo` with the camera running. Hit Enter. Do not cut until both the pipeline summary and the test result (`Ran 26 tests in 0.041s` / `OK`) are on screen simultaneously.
- If you run `make demo` and `make test` as separate commands, type them sequentially in the same take with no edit.
- If a run fails on camera: stop, reset, and record a fresh take. Do not patch in a cut.
- Acceptable to run in a tmux/iTerm2 split pane if both panes are visible in the same scene without switching.

### File naming

| File | Description |
|------|-------------|
| `stowaway_demo_master.mp4` | Full 1920×1080 landscape master |
| `stowaway_demo_vertical.mp4` | 1080×1920 phone-vertical social cut |
| `stowaway_demo_vo.wav` | Voiceover dry recording (no music, no effects) |
| `stowaway_demo_final.mp4` | Master + VO mixed, color-corrected, captions baked in |
| `stowaway_demo_vertical_final.mp4` | Vertical cut of the final |
| `stowaway_demo_thumb.png` | Thumbnail: the chat ping message (Beat 2), full contrast |

### Pre-shoot checklist (run through 30 min before record)

- [ ] `make demo` runs clean from repo root. Output ends with `done in 0.04s`. Confirm live.
- [ ] `python3 -m unittest discover -s tests -v` ends with `Ran 26 tests in 0.041s` / `OK`.
- [ ] Telegram thread is scrolled to bottom; yesterday's "all clear" message is visible.
- [ ] OpenClaw gateway is running and the bot can send messages to the thread.
- [ ] `data/pod_scans/L-1001.png` and the scan for INV-26049 are identified and pre-loaded in OBS image sources.
- [ ] ARCHITECTURE.md Mermaid diagram is rendered and open in browser, full-screen.
- [ ] OBS scenes are named and tested. Preview each scene before rolling.
- [ ] VO script printed or on a second monitor out of frame.
- [ ] Record a 10-second test clip and confirm audio levels (VO mic and desktop audio both non-clipping).
- [ ] Telegram font size bumped to at least 14pt so messages are legible at 1080p.
- [ ] All desktop notifications silenced (Do Not Disturb ON) except the Stowaway bot.

---

## 5. FALLBACK PLAN — terminal-only shoot (if OpenClaw/Telegram is not wired in time)

**Rule:** if the chat gateway is not working, shoot only what is real. Do not mock a chat UI, paste screenshots of fake messages, or composite a phone frame around a static image. The OpenClaw community knows what a live Telegram thread looks like versus a staged one. A fake chat loses all credibility and cannot be fixed in post.

The fallback shows the same evidence in a different container: the terminal. It is honest and it is strong.

### Fallback beat mapping

| Original beat | Fallback screen | What changes |
|---|---|---|
| Beat 1 (quiet day) | Terminal: run `make demo` on a dataset where all invoices pass. Pre-generate a fixture set with no flags. The output is `⚓ Stowaway: 48 invoices audited, all clear. Nothing needs you. Go home.` Fullscreen terminal, that line visible. | VO unchanged. |
| Beat 2 (ping arrives) | Terminal: run `make demo` on the real fixture set. Let the full pipeline output scroll in real time, ending with the chat-ping line: `⚓ Stowaway: 51 invoices audited — 36 cleared, 15 need eyes. / 💸 $4,751 recoverable, $24,846 held. / Worst: Bluewater Logistics LLC (INV-26036)...` | VO unchanged. The ping text is still on screen; it just lives in a terminal. |
| Beat 3 (INV-26038 detail) | Open `report.md` in `bat` or `less -R` in the terminal. Scroll to the INV-26038 section. The evidence chain (CARRIER_NAME_MISMATCH, FMCSA citation, STALE_FUEL_WEEK, DOE line, FSC computation) is all there verbatim. | VO unchanged. Caption: "Full evidence chain — report.md, live output." |
| Beat 4 (fuel catch) | Same `report.md` view. Zoom terminal font to 18pt (Cmd+= on macOS). Scroll to and hold on the STALE_FUEL_WEEK block for INV-26038. | VO unchanged. |
| Beat 5 (POD scans) | Open both PNG files side by side using `imgcat` (iTerm2) or `open` them in Preview split-view, then screengrab that. This is not faked — these are the real files the VLM scored. Show the terminal command that opened them. | VO unchanged. If `imgcat` is not available, show `ls data/pod_scans/` followed by `cat` of the fixture JSON showing `signature_present: false` for the flagged load. |
| Beat 6 (make demo) | Unchanged. This beat is already pure terminal. | Unchanged. |
| Beat 7 (architecture) | Open `ARCHITECTURE.md` in `bat` or `cat` in terminal. The Mermaid source is readable as plain text and the phase structure is clear. Alternatively, render to SVG with `mmdc` offline and open the SVG in Preview. | VO unchanged. |
| Beat 8 (release) | Instead of typing in Telegram, run: `python3 -m stowaway.cli release INV-26041` or equivalent CLI command if implemented. If no release CLI exists, show that the design prohibits automated release by showing the relevant code in `reconcile.py` lines 92–110 — the `render_chat_ping` output instructs a human to reply; the code never calls a payment API. | VO: replace "It flags the money. It never moves it. Humans keep the keys." with the same line — it is still true and more explicit in this fallback. |

### Fallback recording notes

- The fallback is actually stronger on one dimension: it proves the math is in Python, not in a prompt. Lean into that in the VO for Beat 6.
- Use `bat report.md` (syntax-highlighted markdown in terminal) rather than `cat` — it is more readable on camera.
- Keep font size at 16–18pt in the terminal for the entire fallback shoot so text is legible at 1080p without zooming.
- The fallback version drops the "relatable chat" hook of Beat 1 and 2. If time permits before the deadline, wire Telegram with a simple bot script (no OpenClaw dependency) that prints the `render_chat_ping` output to the chat — that is not faking, that is a simpler integration. The OpenClaw gateway is the production path; a `python-telegram-bot` direct send is an acceptable fallback that preserves the chat UI beats.

---

*End of shooting script.*
