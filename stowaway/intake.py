"""Phase 1 — INTAKE.

Pull documents in whatever shape they arrive, emit canonical records.
"Same fields, same shape, every time."

Replay mode loads the committed synthetic dataset (data/). Live mode pulls
invoice + POD attachments from a Gmail shared inbox via Composio Tool Router
and reads POD scans with a VLM on Nebius Token Factory.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Invoice, LoadRecord, PodExtract


def load_dataset(data_dir: Path) -> tuple[dict[str, LoadRecord], list[Invoice], dict[str, PodExtract]]:
    loads = {
        d["load_id"]: LoadRecord.from_dict(d)
        for d in json.loads((data_dir / "loads.json").read_text())
    }
    invoices = [Invoice.from_dict(d) for d in json.loads((data_dir / "invoices.json").read_text())]
    pods = {
        d["load_id"]: PodExtract.from_dict(d)
        for d in json.loads((data_dir / "pods.json").read_text())
    }
    return loads, invoices, pods


# --------------------------------------------------------------- live (Mikey)

def pull_inbox_live() -> list[Invoice]:
    # TODO(Mikey, handoff task #3): Composio Tool Router (the GA flagship, not
    # the legacy SDK) -> Gmail shared inbox: list unread with attachments,
    # download invoice PDFs + POD images. Least-privilege scopes only
    # (gmail.readonly is enough for intake). Their May-2026 incident makes
    # auth hygiene a scoreable topic — keep scopes minimal and documented.
    raise NotImplementedError("live inbox intake — handoff task #3")


def read_pod_live(image_path: Path) -> PodExtract:
    # TODO(Mikey, handoff task #4): Nebius Token Factory, OpenAI-compatible
    # chat.completions with image input (Qwen3-VL or best available VLM).
    # Prompt for STRUCTURED output matching PodExtract fields; record the
    # response as a fixture so replay mode keeps working. Open models only.
    if not os.environ.get("NEBIUS_API_KEY"):
        raise RuntimeError("live POD vision requires NEBIUS_API_KEY")
    raise NotImplementedError("live POD vision — handoff task #4")
