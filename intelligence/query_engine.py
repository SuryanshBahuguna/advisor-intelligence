from intelligence.vector_store import query as vs_query


class QueryEngine:
    def __init__(self, collection):
        self.collection = collection

    def ask(self, q: str, top_k: int = 5):
        question = (q or "").strip()
        if not question:
            return {"results": []}

        raw = vs_query(question, n_results=top_k)

        metas = (raw.get("metadatas") or [[]])[0]
        results = []

        seen = set()
        for m in metas:
            client = m.get("client_name") or m.get("client") or "Unknown Client"
            source = m.get("source_file") or m.get("file_name") or m.get("source") or "unknown_source"

            key = (client, source)
            if key in seen:
                continue
            seen.add(key)

            results.append({"client": client, "source": source})

        return {"results": results}



