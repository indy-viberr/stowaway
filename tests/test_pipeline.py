"""End-to-end: the full replay audit must reproduce the planted answer key exactly.

data/answer_key.json lists every fraud planted in the synthetic dataset;
the pipeline must find all of it and nothing else. This is the falsifiable
version of the project's central claim.
"""
import json
import tempfile
import unittest
from pathlib import Path

from stowaway.cli import ROOT, audit


class TestPipeline(unittest.TestCase):
    def test_replay_audit_matches_answer_key(self):
        answer_key = json.loads((ROOT / "data" / "answer_key.json").read_text())
        out = Path(tempfile.mkdtemp()) / "report.md"
        report = audit("replay", ROOT / "data", out)

        found = {
            v.invoice.invoice_id: sorted({f.rule for f in v.flags})
            for v in report.verdicts if v.flags
        }
        self.assertEqual(found, answer_key)
        self.assertTrue(out.exists())
        self.assertGreater(report.leakage_cents, 0)
        self.assertGreater(report.at_risk_cents, 0)


if __name__ == "__main__":
    unittest.main()
