import json
from pathlib import Path

from chaser.state_machine import get_next_state

TASKS_PATH = Path("data/doc_tasks.json")
OUT_PATH = Path("data/doc_tasks_updated.json")

def recommend_action(task, next_state: str) -> str:
    channel = task.get("channel", "email")
    target = task.get("target", "client")

    if next_state == "ESCALATED":
        if target == "provider":
            return f"Escalate to phone follow-up + resend email ({channel})"
        if target == "client":
            return f"Escalate: call + email reminder ({channel})"
        return "Escalate: notify advisor"

    if next_state == "REMINDER_SENT":
        return f"Send follow-up via {channel}"

    return f"Send initial request via {channel}"

if __name__ == "__main__":
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))

    updated = []
    for t in tasks:
        next_state = get_next_state({
            "status": t["status"].upper() if t["status"].islower() else t["status"],
            "due_date": t["due_date"]
        })

        action = recommend_action(t, next_state)
        updated.append({**t, "next_state": next_state, "recommended_action": action})

    OUT_PATH.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    print(f"Updated tasks saved to {OUT_PATH}")

    by_client = {}
    for u in updated:
        by_client.setdefault(u["client_name"], []).append(u)

    for client, items in by_client.items():
        print(f"\nCLIENT: {client}")
        for it in items[:10]:
            print(f"- {it['item_name']} | {it['required_for']} | {it['target']} | {it['priority']}")
            print(f"  due: {it['due_date']} | state: {it['status']} -> {it['next_state']}")
            print(f"  action: {it['recommended_action']}")
            print(f"  source: {it['source_doc']}")
