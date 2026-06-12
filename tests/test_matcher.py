"""Tests for the deterministic core. Plain unittest — runs under pytest too."""
import unittest

from stowaway.matcher import Tolerances, find_duplicate_billing, match_invoice
from stowaway.models import (
    AccessorialAllowance, Invoice, InvoiceLine, LoadRecord, PodExtract,
)


def mk_load(**kw) -> LoadRecord:
    base = dict(
        load_id="L-1", lane="A -> B", pickup_date="2026-06-01",
        carrier_mc="412887", carrier_name="Meridian Haulage Inc",
        agreed_linehaul_cents=200000, consignee="Westgate DC",
        accessorials_allowed=[AccessorialAllowance("DET", 40000)],
    )
    base.update(kw)
    return LoadRecord(**base)


def mk_invoice(lines, **kw) -> Invoice:
    base = dict(
        invoice_id="INV-1", invoice_date="2026-06-09",
        carrier_mc="412887", carrier_name="Meridian Haulage Inc", load_id="L-1",
    )
    base.update(kw)
    return Invoice(lines=[InvoiceLine(*l) for l in lines], **base)


def mk_pod(**kw) -> PodExtract:
    base = dict(load_id="L-1", present=True, signature_present=True,
                signature_legibility=0.9, date_legible=True,
                consignee_name="Westgate DC", doc_quality=0.8)
    base.update(kw)
    return PodExtract(**base)


CLEAN_LINES = [("LINEHAUL", "lh", 200000), ("FSC", "fuel", 40000)]


class TestMatcher(unittest.TestCase):
    def run_match(self, invoice, load=None, pod=...):
        load = load or mk_load()
        pods = {} if pod is None else {load.load_id: (mk_pod() if pod is ... else pod)}
        return match_invoice(invoice, {load.load_id: load}, pods)

    def test_clean_invoice_no_flags(self):
        self.assertEqual(self.run_match(mk_invoice(CLEAN_LINES)), [])

    def test_unknown_load_is_critical(self):
        flags = self.run_match(mk_invoice(CLEAN_LINES, load_id="L-999"))
        self.assertEqual([f.rule for f in flags], ["UNKNOWN_LOAD"])
        self.assertEqual(flags[0].dollar_impact_cents, 240000)

    def test_linehaul_variance_over_tolerance(self):
        inv = mk_invoice([("LINEHAUL", "lh", 218000), ("FSC", "fuel", 40000)])
        flags = self.run_match(inv)
        self.assertIn("LINEHAUL_VARIANCE", [f.rule for f in flags])
        self.assertEqual(flags[0].dollar_impact_cents, 18000)

    def test_linehaul_variance_within_tolerance_passes(self):
        # 1% of 200000 = 2000; +1500 is inside
        inv = mk_invoice([("LINEHAUL", "lh", 201500), ("FSC", "fuel", 40000)])
        self.assertEqual(self.run_match(inv), [])

    def test_unauthorized_accessorial(self):
        inv = mk_invoice(CLEAN_LINES + [("LIFTGATE", "lift", 15000)])
        flags = self.run_match(inv)
        self.assertEqual([f.rule for f in flags], ["UNAUTHORIZED_ACCESSORIAL"])

    def test_authorized_accessorial_within_cap_passes(self):
        inv = mk_invoice(CLEAN_LINES + [("DET", "detention", 30000)])
        self.assertEqual(self.run_match(inv), [])

    def test_accessorial_over_cap(self):
        inv = mk_invoice(CLEAN_LINES + [("DET", "detention", 55000)])
        flags = self.run_match(inv)
        self.assertEqual([f.rule for f in flags], ["ACCESSORIAL_OVER_CAP"])
        self.assertEqual(flags[0].dollar_impact_cents, 15000)

    def test_duplicate_accessorial(self):
        inv = mk_invoice(CLEAN_LINES + [("DET", "det", 20000), ("DET", "det", 20000)])
        self.assertIn("DUPLICATE_ACCESSORIAL", [f.rule for f in self.run_match(inv)])

    def test_pod_missing(self):
        flags = self.run_match(mk_invoice(CLEAN_LINES), pod=None)
        self.assertEqual([f.rule for f in flags], ["POD_MISSING"])

    def test_pod_signature_missing(self):
        pod = mk_pod(signature_present=False, signature_legibility=0.0)
        flags = self.run_match(mk_invoice(CLEAN_LINES), pod=pod)
        self.assertEqual([f.rule for f in flags], ["POD_SIGNATURE_MISSING"])

    def test_pod_illegible(self):
        pod = mk_pod(signature_legibility=0.2)
        flags = self.run_match(mk_invoice(CLEAN_LINES), pod=pod)
        self.assertEqual([f.rule for f in flags], ["POD_ILLEGIBLE"])

    def test_consignee_mismatch(self):
        pod = mk_pod(consignee_name="Eastline Paper Products")
        flags = self.run_match(mk_invoice(CLEAN_LINES), pod=pod)
        self.assertEqual([f.rule for f in flags], ["CONSIGNEE_MISMATCH"])

    def test_consignee_normalization_not_overeager(self):
        pod = mk_pod(consignee_name="WESTGATE D.C.")
        self.assertEqual(self.run_match(mk_invoice(CLEAN_LINES), pod=pod), [])


class TestDuplicateBilling(unittest.TestCase):
    def test_same_load_two_invoices_flags_later_one(self):
        a = mk_invoice(CLEAN_LINES, invoice_id="INV-A", invoice_date="2026-06-05")
        b = mk_invoice(CLEAN_LINES, invoice_id="INV-B", invoice_date="2026-06-09")
        flags = find_duplicate_billing([b, a])
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].invoice_id, "INV-B")
        self.assertEqual(flags[0].rule, "DUPLICATE_BILLING")

    def test_distinct_loads_no_flags(self):
        a = mk_invoice(CLEAN_LINES, invoice_id="INV-A", load_id="L-1")
        b = mk_invoice(CLEAN_LINES, invoice_id="INV-B", load_id="L-2")
        self.assertEqual(find_duplicate_billing([a, b]), [])


if __name__ == "__main__":
    unittest.main()
