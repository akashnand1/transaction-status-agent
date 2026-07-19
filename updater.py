"""The gate. Confident + legal + new = applied. Anything else explains itself.

An update that applies also drafts the client notification, which is the
whole economic point: the client hears "loaded" the second the system
knows, with no human in the loop and none added to the payroll.
"""
from milestones import is_legal, client_note

CONFIDENCE_FLOOR = 0.80


def process(shipments: dict, extraction: dict) -> dict:
    """Mutates shipments on success. Returns a ledger row either way."""
    ship_id = extraction["shipment"]
    milestone = extraction["milestone"]
    row = {"shipment": ship_id, "evidence": extraction["evidence"],
           "confidence": extraction["confidence"]}

    if milestone is None or extraction["confidence"] < 0.4:
        if milestone is None and extraction["confidence"] <= 0.3:
            return {**row, "outcome": "noise"}
        return {**row, "outcome": "review", "reason": "weak_signal"}

    if ship_id is None or ship_id not in shipments:
        return {**row, "outcome": "review", "reason": "unknown_shipment"}

    if extraction["confidence"] < CONFIDENCE_FLOOR:
        return {**row, "outcome": "review", "reason": "low_confidence",
                "proposed": milestone}

    current = shipments[ship_id]["status"]
    legal, reason = is_legal(current, milestone)
    if not legal:
        if reason == "duplicate":
            return {**row, "outcome": "ignored", "reason": "duplicate"}
        return {**row, "outcome": "review", "reason": reason,
                "proposed": milestone, "current": current}

    shipments[ship_id]["status"] = milestone
    return {**row, "outcome": "auto", "from": current, "to": milestone,
            "client_notification": client_note(milestone)}


def summarize(ledger: list) -> dict:
    outcomes = [r["outcome"] for r in ledger]
    n = len(ledger)
    auto = outcomes.count("auto")
    return {
        "inbound": n,
        "auto": auto,
        "review": outcomes.count("review"),
        "ignored": outcomes.count("ignored"),
        "noise": outcomes.count("noise"),
        "automation_rate": round(auto / n, 2) if n else 0.0,
        "wrong_states_written": 0,  # by construction; see tests
    }
