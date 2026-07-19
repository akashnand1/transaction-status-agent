# transaction-status-agent

The part of an AI assistant portfolio nobody demos and everybody depends on: keeping the transaction record true while trucks move. This is a working miniature of a transaction management capability I shipped in production, where it automated roughly 25% of all shipment status updates with zero added operational overhead. The clients found out their truck was loaded because the system already knew, not because someone remembered to type it in.

Rebuilt from scratch on invented data. Offline, zero API keys, standard library only.

## Why this problem is worth an agent

A freight marketplace lives or dies on one question asked ten thousand times a day: where is my shipment? The answer usually exists, trapped in a driver's voice note, a WhatsApp photo of a stamped delivery note, a supervisor's two-word message. Operations teams burn hours transcribing that into the system, late and unevenly, and every delay becomes a client call.

The insight that made this work in production: **you do not need to automate all updates to change the economics.** Every update the system captures on its own is a client notification that goes out instantly and an operations minute returned. Automating the confident quarter of the volume, and never being wrong inside it, beats automating 80% with apologies.

## The design rule: state machine in code, language in the model

The LLM's job ends at "this message says the truck was loaded, and I am 0.9 sure." Whether LOADED is a legal next state for this shipment, whether it already happened, what to tell the client: that is deterministic code, testable and boring on purpose.

- `milestones.py` is the shipment state machine: ASSIGNED, AT_PICKUP, LOADED, IN_TRANSIT, AT_DELIVERY, DELIVERED, POD_SUBMITTED. Forward-only transitions with explicit skip rules (a truck can jump to IN_TRANSIT if we missed LOADED, but nothing moves backwards).
- `extract.py` reads inbound messages (driver voice-note transcripts, vendor texts, OCR'd documents) and emits (shipment, milestone, confidence, evidence). Deterministic rules stand in for the model; `extract_with_model` is the one-function LLM seam.
- `updater.py` is the gate. An update applies itself only when the extraction is confident AND the transition is legal AND it is not a duplicate. Everything else goes to a review queue with the reason attached. Applied updates draft the client notification automatically.
- `demo.py` replays a day of 20 inbound messages across 6 shipments and prints the ledger: what auto-applied, what queued, what was ignored as noise, and the automation rate.

## Run it

```bash
python demo.py           # a day of messages -> updated shipments + the ledger
python -m unittest -v    # tests, including the ones that matter: illegal transitions never apply
```

## Sample output

```
SHP-104  LOADED -> IN_TRANSIT   auto    (voice: "SHP-104 left jebel ali gate now", conf 0.81)
         client notified: "Your shipment is on the move."
SHP-101  REVIEW  illegal_transition    (text: "SHP-101 loaded", conf 0.9)
SHP-105  REVIEW  weak_signal           (voice: "boss SHP-105 reaching soon inshallah", conf 0.5)
SHP-104  ignored: duplicate            (text: "SHP-104 on the way")

Day summary: 20 inbound · 10 auto-applied · 5 queued for review · 1 duplicate · 4 noise
Automation rate: 50% of inbound messages, 0 wrong states written
```

## Boundaries

Personal project. Invented shipments, invented messages, public geography, no company code or data. The production system this mirrors is described only by its shape. The conviction is mine: an agent that touches a system of record earns that right one guarded transition at a time.

MIT licensed.
