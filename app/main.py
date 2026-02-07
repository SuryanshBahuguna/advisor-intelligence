from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import json
from fastapi.staticfiles import StaticFiles
from chaser.state_machine import get_next_state

from ingestion.docx_reader import load_source_docs
from ingestion.build_tasks_from_docs import make_client_id, sane_anchor_date
from ingestion.extractor import (
    guess_client_name,
    find_any_date,
    parse_date_hint,
    extract_presence,
    build_tasks,
)

from intelligence.query_engine import QueryEngine
from intelligence.vector_store import get_db

app = FastAPI()

# In production (same-origin), CORS isn't required, but keeping localhost helps dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_DIR = Path("data/source_docs")
EXTRACTED_DIR = Path("data/extracted")
TASKS_FILE = Path("data/doc_tasks.json")

SOURCE_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        out = SOURCE_DIR / f.filename
        with out.open("wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved.append(f.filename)
    return {"saved": saved}


@app.post("/run")
def run():
    docs = load_source_docs(str(SOURCE_DIR))
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
            "presence": presence,
        }

        (EXTRACTED_DIR / f"{client_id}.json").write_text(
            json.dumps(extracted, indent=2), encoding="utf-8"
        )

        tasks = build_tasks(client_id, client_name, file_name, presence, anchor)
        all_tasks.extend(tasks)

    TASKS_FILE.write_text(json.dumps(all_tasks, indent=2), encoding="utf-8")
    return {"tasks_count": len(all_tasks)}


@app.get("/tasks")
def tasks():
    if not TASKS_FILE.exists():
        return {"tasks": []}
    return {"tasks": json.loads(TASKS_FILE.read_text(encoding="utf-8"))}


@app.get("/chaser/tasks")
def chaser_tasks():
    if not TASKS_FILE.exists():
        return []

    tasks_list = json.loads(TASKS_FILE.read_text(encoding="utf-8"))

    grouped = {}
    for t in tasks_list:
        client = t.get("client_name", "Unknown")
        grouped.setdefault(client, [])

        cur = t.get("status", "NOT_STARTED")
        due = t.get("due_date")
        nxt = get_next_state({"status": cur, "due_date": due})

        grouped[client].append(
            {
                "item": t.get("item_name"),
                "state": f"{cur} -> {nxt}",
                "due_date": due,
                "action": t.get("reason"),
                "source": t.get("source_doc"),
                "target": t.get("target"),
                "priority": t.get("priority"),
                "required_for": t.get("required_for"),
            }
        )

    out = []
    for client, items in grouped.items():
        out.append({"client": client, "tasks": items})

    return out


@app.post("/chaser/run")
def chaser_run():
    run()
    return {"ok": True}


@app.get("/intelligence/ask")
def intelligence_ask(q: str):
    db = get_db()
    engine = QueryEngine(db)
    return engine.ask(q)


# ✅ IMPORTANT: mount UI *after* API routes so API endpoints still work
UI_DIST = Path(__file__).resolve().parents[1] / "ui" / "dist"
if UI_DIST.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIST), html=True), name="ui")
