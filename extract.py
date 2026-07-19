"""Message -> (shipment_id, milestone, confidence, evidence).

Deterministic rules stand in for the model so the repo runs offline.
`extract_with_model` is the LLM seam: swap its body for a model call
returning the same shape, and nothing downstream changes. Downstream
trusts confidence numbers, not the extractor.
"""
import re

CHANNEL_FACTOR = {"text": 1.0, "voice": 0.9, "ocr": 0.85}

# phrase -> (milestone, base confidence). Ordered: first match wins,
# most specific first.
PATTERNS = [
    (r"pod|proof of delivery|delivery note (submitted|uploaded)", "POD_SUBMITTED", 0.95),
    (r"delivered|offloaded|unload(ed|ing) done", "DELIVERED", 0.95),
    (r"(reached|at) (the )?(delivery|destination|receiver)", "AT_DELIVERY", 0.9),
    (r"left .* gate|departed|on the way|on the road|moving now", "IN_TRANSIT", 0.9),
    (r"load(ing|ed).*(done|complete|finish)|loaded", "LOADED", 0.9),
    (r"delivery note stamped|stamped", "LOADED", 0.9),
    (r"(reached|at) (the )?(pickup|loading|warehouse|port)", "AT_PICKUP", 0.9),
    (r"reaching soon|almost there|near|close by", None, 0.55),   # a hint, not a fact
    (r"traffic|salam|thanks|ok boss|invoice|payment", None, 0.2),  # noise
]

SHIPMENT_RE = re.compile(r"\b(SHP-\d+)\b", re.I)


def extract_with_model(message: dict) -> dict:
    """The seam. Returns {shipment, milestone, confidence, evidence}."""
    body = message["body"].lower()
    factor = CHANNEL_FACTOR[message["channel"]]
    ship = SHIPMENT_RE.search(message["body"])
    shipment = ship.group(1).upper() if ship else message.get("thread_shipment")

    for pattern, milestone, base in PATTERNS:
        if re.search(pattern, body):
            return {
                "shipment": shipment,
                "milestone": milestone,
                "confidence": round(base * factor, 2),
                "evidence": f"{message['channel']}: \"{message['body'][:60]}\"",
            }
    return {"shipment": shipment, "milestone": None, "confidence": 0.0,
            "evidence": f"{message['channel']}: no status signal"}
