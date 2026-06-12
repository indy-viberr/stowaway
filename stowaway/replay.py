"""Record/replay layer for every external call.

Why this exists: an audit pipeline must be testable offline and
deterministically. Every external dependency (Tavily, Token Factory) is
wrapped so the full pipeline runs end-to-end from committed JSON fixtures
with ZERO keys and ZERO third-party packages:

    make demo        # replay mode, no network, no keys
    make demo-live   # same pipeline, real APIs (.env required)

In live mode, responses are recorded to fixtures so replay stays current.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FixtureStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str) -> Path:
        return self.root / f"{namespace}.json"

    def load(self, namespace: str) -> dict[str, Any]:
        p = self._path(namespace)
        if not p.exists():
            return {}
        return json.loads(p.read_text())

    def get(self, namespace: str, key: str) -> Any | None:
        return self.load(namespace).get(key)

    def put(self, namespace: str, key: str, value: Any) -> None:
        data = self.load(namespace)
        data[key] = value
        self._path(namespace).write_text(json.dumps(data, indent=2, sort_keys=True))


class ReplayMissError(KeyError):
    """Raised in replay mode when a fixture is missing — fail loudly, not quietly."""

    def __init__(self, namespace: str, key: str):
        super().__init__(
            f"Replay fixture miss: {namespace}[{key!r}]. "
            f"Run once in live mode to record it, or add the fixture by hand."
        )
