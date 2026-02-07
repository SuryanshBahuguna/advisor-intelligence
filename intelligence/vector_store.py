import chromadb
from sentence_transformers import SentenceTransformer

_client = chromadb.PersistentClient(path="vectordb")
_collection = _client.get_or_create_collection(name="advisor_memory")
_model = SentenceTransformer("all-MiniLM-L6-v2")


def add_text(doc_id: str, text: str, metadata: dict):
    embedding = _model.encode(text).tolist()
    _collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata],
        embeddings=[embedding],
    )


def query(question: str, n_results: int = 3):
    embedding = _model.encode(question).tolist()
    return _collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
    )


def get_db():
    return _collection
