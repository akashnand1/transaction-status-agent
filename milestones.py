"""Shipment state machine. Deterministic, forward-only, boring on purpose.

The language model never touches this file. It proposes; this disposes.
"""

ORDER = ["ASSIGNED", "AT_PICKUP", "LOADED", "IN_TRANSIT",
         "AT_DELIVERY", "DELIVERED", "POD_SUBMITTED"]

# How many stages a single update may skip. Real feeds miss milestones
# (nobody messages "arrived at pickup" from a loading bay), so one skip
# is legal; teleporting from ASSIGNED to DELIVERED is not.
MAX_SKIP = 2

CLIENT_NOTES = {
    "AT_PICKUP": "Your truck has arrived at the pickup location.",
    "LOADED": "Loading is complete. Your shipment is ready to depart.",
    "IN_TRANSIT": "Your shipment is on the move.",
    "AT_DELIVERY": "Your truck has arrived at the delivery location.",
    "DELIVERED": "Your shipment has been delivered.",
    "POD_SUBMITTED": "Proof of delivery has been submitted and is under review.",
}


def is_legal(current: str, proposed: str) -> tuple:
    """(legal, reason). Forward-only, bounded skip, no repeats."""
    if proposed not in ORDER:
        return False, f"unknown_milestone({proposed})"
    ci, pi = ORDER.index(current), ORDER.index(proposed)
    if pi == ci:
        return False, "duplicate"
    if pi < ci:
        return False, "illegal_transition"          # time does not run backwards
    if pi - ci > MAX_SKIP:
        return False, f"skip_too_large({current}->{proposed})"
    return True, "ok"


def client_note(milestone: str) -> str:
    return CLIENT_NOTES.get(milestone, "")
