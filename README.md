Agentic Advisor Chaser – End-to-End AI Assistant for Financial Advisers
Overview

Agentic Advisor Chaser is an AI-powered system that:

Reads unstructured adviser documents (Fact Finds, Meeting Notes, Client Docs)
Automatically detects what information is missing
Creates intelligent chaser tasks with due dates
Tracks state progression (On-Track → Reminder → Escalated)
Allows advisers to query all documents using natural language
Presents everything in a clear, traffic-light UI

This solves a real operational problem:
Advisers miss follow-ups not because of intent, but because information is fragmented across documents.

In financial advice:

Client info arrives late, incomplete, and scattered
LOAs, pension data, ISA details, risk profiles are often missing
Chasing is manual, inconsistent, and error-prone
Compliance risk increases as deadlines are missed
This system turns documents into an agentic workflow engine.


 Key Capabilities
1. Intelligent Document Ingestion

Accepts .docx adviser documents

Extracts:

Client name
Key dates (meeting / document dates)
Presence or absence of required data points

2. Anchor Date & Due Date Logic

Each document provides an anchor date (e.g. meeting date)
Task due dates are calculated as offsets from that anchor
If no valid date exists, a safe fallback is applied

##This makes deadlines context-aware, not static.

3. Agentic Chaser Task Generation

For each client, the system auto-creates tasks like:

Missing pension valuations
Missing transfer values
Missing exit penalties
Missing risk profile
Missing ISA allowance details
LOA request generation at the right stage


Each task includes:

Priority (high / medium / low)
Target (client / provider / adviser)
Reason (why this task exists)
Due date
Required-for stage (pre-advice, advice, review)

4. Chaser State Machine (Core Intelligence)

Every task moves through states:

State	Meaning
ON TRACK	Due date not reached
REMINDER	Due date approaching
ESCALATED	Due date missed

States are computed dynamically using:
Task status
Due date
Current date

###Fully deterministic.

5. Traffic-Light UI (Red / Amber / Green)

Task-level status: each task shows its own severity
Client-level status: worst task determines client severity

Colours:

🟢 Green = On Track

🟠 Amber = Needs Reminder

🔴 Red = Escalated

This lets advisers instantly see:
Which client needs attention right now?

6. Query Intelligence (Natural Language Search)

Advisers can ask questions like:

“Who discussed inheritance tax?”

“Which clients mentioned pensions?”

“Which meetings talked about ISA planning?”

Logic behind query engine:

Documents are embedded using sentence transformers
Stored in a vector database
Queried via semantic similarity
Results mapped back to clients + source docs



 UI & Backend Architecture

Backend
FastAPI

Frontend
React + Vite


📂 Project Structure
advisor-intelligence/
├── app/
│   └── main.py              # FastAPI app (API + UI mount)
├── ingestion/
│   ├── docx_reader.py       # Reads .docx files
│   ├── extractor.py         # Detects missing info
│   └── build_tasks_from_docs.py
├── chaser/
│   └── state_machine.py     # Reminder / Escalation logic
├── intelligence/
│   ├── vector_store.py      # Embeddings + vector DB
│   └── query_engine.py      # Natural language search
├── data/
│   ├── source_docs/         # Input adviser documents
│   └── doc_tasks.json       # Generated tasks (demo-ready)
├── ui/
│   ├── src/
│   └── dist/                # Built frontend (served by FastAPI)

▶️ How to Run Locally (Step-by-Step)
1️⃣ Backend Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Backend runs on:

http://localhost:8000

2️⃣ Frontend Setup
cd ui
npm install
npm run dev


UI runs on:

http://localhost:5173


Create ui/.env:

VITE_API_BASE=http://localhost:8000


Restart UI after adding .env.

## How to Ingest New Documents


To ingest new files:

Copy .docx files into:

data/source_docs/


Run ingestion:

python -m ingestion.build_tasks_from_docs

You do NOT need to run `load_source_docs` manually.
`load_source_docs` is an internal helper that is automatically executed as part of the ingestion pipeline.

When you run,

python -m ingestion.build_tasks_from_docs

the system will:
1. Load all `.docx` files from `data/source_docs/`
2. Extract plain text from each document
3. Detect missing financial data
4. Generate chaser tasks with due dates
5. Save results to `data/doc_tasks.json`

This single command handles the entire ingestion process.


After running it, refresh UI and tasks will regenerate automatically.

Deployment Notes:

Deployed on Render (https://advisor-intelligence-api.onrender.com)
UI + API served from the same origin
Tasks are preloaded to avoid empty state



Why This Is Agentic

This system:

Interprets documents
Detects missing information
Creates actions
Prioritises urgency
Evolves state over time
Surfaces insights via queries



Future Extensions:

Email / CRM integrations
Adviser notifications
Multi-adviser dashboards
Compliance audit trails
LLM-based reasoning on next best action

Summary:

Agentic Advisor Chaser demonstrates how AI can:
Turn unstructured documents into workflows
Reduce adviser operational risk
Improve compliance outcomes
Scale advisory operations intelligently