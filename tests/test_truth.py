"""External-truth checks against in-memory fixtures."""
import tempfile
import unittest
from pathlib import Path

from stowaway.models import Invoice, InvoiceLine, LoadRecord
from stowaway.replay import FixtureStore, ReplayMissError
from stowaway.truth import TruthClient, fsc_pct_for_price, week_monday


def mk_client(fmcsa=None, doe=None) -> TruthClient:
    tmp = Path(tempfile.mkdtemp())
    store = FixtureStore(tmp)
    for k, v in (fmcsa or {}).items():
        store.put("fmcsa", k, v)
    for k, v in (doe or {}).items():
        store.put("doe_diesel", k, {"price": v})
    return TruthClient(store, mode="replay")


def mk_invoice(mc="412887", name="Meridian Haulage Inc", fsc=40000) -> Invoice:
    return Invoice(
        invoice_id="INV-1", invoice_date="2026-06-09", carrier_mc=mc,
        carrier_name=name, load_id="L-1",
        lines=[InvoiceLine("LINEHAUL", "lh", 200000), InvoiceLine("FSC", "fuel", fsc)],
    )


def mk_load() -> LoadRecord:
    return LoadRecord(
        load_id="L-1", lane="A -> B", pickup_date="2026-06-03",  # Wed -> Monday 06-01
        carrier_mc="412887", carrier_name="Meridian Haulage Inc",
        agreed_linehaul_cents=200000, consignee="Westgate DC",
    )


class TestHelpers(unittest.TestCase):
    def test_week_monday(self):
        self.assertEqual(week_monday("2026-06-03"), "2026-06-01")
        self.assertEqual(week_monday("2026-06-01"), "2026-06-01")
        self.assertEqual(week_monday("2026-06-07"), "2026-06-01")

    def test_fsc_brackets(self):
        self.assertEqual(fsc_pct_for_price(3.55), 0.20)
        self.assertEqual(fsc_pct_for_price(4.11), 0.24)


class TestCarrierChecks(unittest.TestCase):
    def test_active_matching_carrier_is_clean(self):
        c = mk_client(fmcsa={"412887": {
            "found": True, "legal_name": "Meridian Haulage Inc", "authority": "ACTIVE"}})
        self.assertEqual(c.check_carrier(mk_invoice()), [])

    def test_phantom_carrier(self):
        c = mk_client(fmcsa={"998877": {"found": False}})
        flags = c.check_carrier(mk_invoice(mc="998877", name="Bluewater Logistics LLC"))
        self.assertEqual([f.rule for f in flags], ["PHANTOM_CARRIER"])
        self.assertEqual(flags[0].dollar_impact_cents, 240000)

    def test_revoked_authority(self):
        c = mk_client(fmcsa={"884210": {
            "found": True, "legal_name": "Redline Carriers Inc", "authority": "REVOKED"}})
        flags = c.check_carrier(mk_invoice(mc="884210", name="Redline Carriers Inc"))
        self.assertEqual([f.rule for f in flags], ["AUTHORITY_REVOKED"])

    def test_name_mismatch_double_brokering(self):
        c = mk_client(fmcsa={"771455": {
            "found": True, "legal_name": "Garza Trucking LLC", "authority": "ACTIVE"}})
        flags = c.check_carrier(mk_invoice(mc="771455", name="Apex Freight Solutions"))
        self.assertEqual([f.rule for f in flags], ["CARRIER_NAME_MISMATCH"])

    def test_replay_miss_fails_loudly(self):
        c = mk_client()
        with self.assertRaises(ReplayMissError):
            c.check_carrier(mk_invoice(mc="000000"))


class TestFuelChecks(unittest.TestCase):
    def test_correct_week_fsc_passes(self):
        # week of 2026-06-01 @ 3.55 -> 20% of 200000 = 40000
        c = mk_client(doe={"2026-06-01": 3.55})
        self.assertEqual(c.check_fuel_surcharge(mk_invoice(fsc=40000), mk_load()), [])

    def test_stale_week_fsc_flags_with_reverse_match(self):
        # billed at April's 4.11 -> 24% = 48000; current week 3.55 -> 40000
        c = mk_client(doe={"2026-06-01": 3.55, "2026-04-20": 4.11})
        flags = c.check_fuel_surcharge(mk_invoice(fsc=48000), mk_load())
        self.assertEqual([f.rule for f in flags], ["STALE_FUEL_WEEK"])
        self.assertEqual(flags[0].dollar_impact_cents, 8000)
        self.assertIn("2026-04-20", flags[0].summary)

    def test_rounding_grace(self):
        c = mk_client(doe={"2026-06-01": 3.55})
        self.assertEqual(c.check_fuel_surcharge(mk_invoice(fsc=40400), mk_load()), [])


if __name__ == "__main__":
    unittest.main()
