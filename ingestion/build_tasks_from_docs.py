import json
from pathlib import Path
import hashlib
from datetime import datetime, timedelta

from ingestion.docx_reader import load_source_docs
from ingestion.extractor import (
    guess_client_name,
    find_any_date,
    parse_date_hint,
    extract_presence,
    build_tasks,
)

OUT_EXTRACTED = Path("data/extracted")
OUT_TASKS = Path("data/doc_tasks.json")
OUT_EXTRACTED.mkdir(parents=True, exist_ok=True)

def make_client_id(file_name: str) -> str:
    h = hashlib.md5(file_name.encode("utf-8")).hexdigest()[:4].upper()
    return f"DOC_{h}"

def sane_anchor_date(anchor):
    if not anchor:
        return None
    today = datetime.utcnow()
    if anchor.year < 2020:
        return None
    if anchor > today + timedelta(days=365):
        return None
    return anchor

if __name__ == "__main__":
    docs = load_source_docs("data/source_docs")
    all_tasks = []

    for d in docs:
        text = d["text"]
        file_name = d["file_name"]

        client_id = make_client_id(file_name)
        client_name = guess_client_name(text) or file_name.replace(".docx", "")

        date_hint = find_any_date(text)
        anchor = sane_anchor_date(parse_date_hint(date_hint))

        presence = extract_presence(text)

        extracted = {
            "client_id": client_id,
            "client_name": client_name,
            "source_file": file_name,
            "date_hint": date_hint,
            "anchor_date": anchor.date().isoformat() if anchor else None,
            "presence": presence
        }

        (OUT_EXTRACTED / f"{client_id}.json").write_text(
            json.dumps(extracted, indent=2),
            encoding="utf-8"
        )

        tasks = build_tasks(client_id, client_name, file_name, presence, anchor)
        all_tasks.extend(tasks)

        print(f"{file_name} -> {len(tasks)} tasks (anchor={extracted['anchor_date']})")

    OUT_TASKS.write_text(json.dumps(all_tasks, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_tasks)} tasks to {OUT_TASKS}")
