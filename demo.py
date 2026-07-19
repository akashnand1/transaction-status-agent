"""Replay a day of messages and print the ledger."""
import copy

from extract import extract_with_model
from updater import process, summarize
from fixtures import SHIPMENTS, MESSAGES


def main():
    shipments = copy.deepcopy(SHIPMENTS)
    ledger = []
    for msg in MESSAGES:
        row = process(shipments, extract_with_model(msg))
        ledger.append(row)
        if row["outcome"] == "auto":
            print(f"{row['shipment']}  {row['from']} -> {row['to']:<14} auto   ({row['evidence']}, conf {row['confidence']})")
            print(f"         client notified: \"{row['client_notification']}\"")
        elif row["outcome"] == "review":
            print(f"{str(row['shipment']):<8} REVIEW  {row['reason']}   ({row['evidence']}, conf {row['confidence']})")
        elif row["outcome"] == "ignored":
            print(f"{row['shipment']}  ignored: duplicate   ({row['evidence']})")
        else:
            print(f"--       noise   ({row['evidence']})")

    s = summarize(ledger)
    print(f"\nDay summary: {s['inbound']} inbound · {s['auto']} auto-applied · "
          f"{s['review']} queued for review · {s['ignored']} duplicates · {s['noise']} noise")
    print(f"Automation rate: {s['automation_rate']:.0%} of inbound messages, "
          f"{s['wrong_states_written']} wrong states written")
    print("\nFinal states:")
    for ship_id, ship in shipments.items():
        print(f"  {ship_id}  {ship['status']:<14} {ship['lane']}")


if __name__ == "__main__":
    main()
