from fastapi import APIRouter
from intelligence.query_engine import ask

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

@router.get("/ask")
def ask_query(q: str):
    results = ask(q)
    return {"question": q, "results": results}
