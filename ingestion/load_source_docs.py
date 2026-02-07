# ingestion/load_source_docs.py

from pathlib import Path
from ingestion.docx_reader import read_docx_text
from intelligence.vector_store import add_text


def ingest_source_docs(folder: str = "data/source_docs"):
    folder_path = Path(folder)

    for fp in folder_path.glob("*.docx"):
        text = read_docx_text(str(fp))
        if not text.strip():
            continue

        doc_id = fp.stem

        add_text(
            doc_id=doc_id,
            text=text,
            metadata={
                "source": fp.name,
                "file_path": str(fp),
                "client_name": fp.stem
            },
        )

        print(f"Indexed: {fp.name}")


if __name__ == "__main__":
    ingest_source_docs()
