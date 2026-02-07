from pathlib import Path
from docx import Document

def read_docx_text(path: str) -> str:
    """Extract plain text from a .docx file."""
    doc = Document(path)
    parts = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            parts.append(t)
    return "\n".join(parts)

def load_source_docs(folder: str = "data/source_docs"):
    """Return list of {file_name, file_path, text} for all .docx in folder."""
    folder_path = Path(folder)
    docs = []
    for fp in folder_path.glob("*.docx"):
        docs.append({
            "file_name": fp.name,
            "file_path": str(fp),
            "text": read_docx_text(str(fp))
        })
    return docs
