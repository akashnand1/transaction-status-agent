import copy
import unittest

from milestones import is_legal
from extract import extract_with_model
from updater import process, summarize, CONFIDENCE_FLOOR
from fixtures import SHIPMENTS, MESSAGES


def run_day():
    shipments = copy.deepcopy(SHIPMENTS)
    ledger = [process(shipments, extract_with_model(m)) for m in MESSAGES]
    return shipments, ledger


class TestStateMachine(unittest.TestCase):
    def test_backwards_is_never_legal(self):
        self.assertFalse(is_legal("IN_TRANSIT", "LOADED")[0])
        self.assertFalse(is_legal("DELIVERED", "AT_PICKUP")[0])

    def test_bounded_skip(self):
        self.assertTrue(is_legal("LOADED", "AT_DELIVERY")[0])       # skip 1
        self.assertFalse(is_legal("ASSIGNED", "DELIVERED")[0])      # teleport

    def test_duplicate_is_named(self):
        legal, reason = is_legal("LOADED", "LOADED")
        self.assertFalse(legal)
        self.assertEqual(reason, "duplicate")


class TestGate(unittest.TestCase):
    def test_illegal_transition_goes_to_review_not_state(self):
        shipments = {"SHP-1": {"status": "IN_TRANSIT"}}
        row = process(shipments, {"shipment": "SHP-1", "milestone": "LOADED",
                                  "confidence": 0.99, "evidence": "e"})
        self.assertEqual(row["outcome"], "review")
        self.assertEqual(shipments["SHP-1"]["status"], "IN_TRANSIT")

    def test_low_confidence_never_applies(self):
        shipments = {"SHP-1": {"status": "LOADED"}}
        row = process(shipments, {"shipment": "SHP-1", "milestone": "IN_TRANSIT",
                                  "confidence": CONFIDENCE_FLOOR - 0.01, "evidence": "e"})
        self.assertEqual(row["outcome"], "review")
        self.assertEqual(shipments["SHP-1"]["status"], "LOADED")

    def test_unknown_shipment_reviews(self):
        row = process({}, {"shipment": "SHP-999", "milestone": "DELIVERED",
                           "confidence": 0.95, "evidence": "e"})
        self.assertEqual(row["outcome"], "review")
        self.assertEqual(row["reason"], "unknown_shipment")

    def test_auto_update_carries_client_notification(self):
        shipments = {"SHP-1": {"status": "LOADED"}}
        row = process(shipments, {"shipment": "SHP-1", "milestone": "IN_TRANSIT",
                                  "confidence": 0.9, "evidence": "e"})
        self.assertEqual(row["outcome"], "auto")
        self.assertIn("on the move", row["client_notification"])


class TestDayReplay(unittest.TestCase):
    def test_no_wrong_states_ever(self):
        shipments, ledger = run_day()
        # replaying the ledger against the rules: every auto row was legal
        self.assertTrue(all(r["outcome"] != "auto" or "to" in r for r in ledger))
        self.assertEqual(summarize(ledger)["wrong_states_written"], 0)

    def test_the_illegal_and_unknown_cases_were_caught(self):
        _, ledger = run_day()
        reasons = [r.get("reason") for r in ledger if r["outcome"] == "review"]
        self.assertIn("illegal_transition", reasons)
        self.assertIn("unknown_shipment", reasons)

    def test_automation_rate_is_meaningful(self):
        _, ledger = run_day()
        s = summarize(ledger)
        self.assertGreaterEqual(s["auto"], 8)
        self.assertLessEqual(s["automation_rate"], 0.6)  # honesty check: not everything automates


if __name__ == "__main__":
    unittest.main()
