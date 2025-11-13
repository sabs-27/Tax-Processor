"""
PDF reading helpers: extract text from PDF files.
Primary approach: PyMuPDF (fitz). Fallback: pdfminer.six if fitz not available.
"""
from typing import List
import os


def extract_text_from_pdf(path: str) -> str:
    path = os.path.abspath(path)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        texts = []
        for page in doc:
            texts.append(page.get_text())
        return "\n".join(texts)
    except Exception:
        # fallback to pdfminer
        try:
            from io import StringIO
            from pdfminer.high_level import extract_text_to_fp
            output = StringIO()
            with open(path, 'rb') as f:
                extract_text_to_fp(f, output)
            return output.getvalue()
        except Exception as e:
            raise RuntimeError('No PDF extraction backend available (install PyMuPDF or pdfminer.six)')


def extract_texts(paths: List[str]) -> str:
    parts = []
    for p in paths:
        if p.lower().endswith('.pdf'):
            parts.append(extract_text_from_pdf(p))
        elif p.lower().endswith('.txt'):
            with open(p, 'r', encoding='utf-8') as f:
                parts.append(f.read())
        else:
            # delegate to ingestion which may handle images
            from ingestion import ingest_paths
            parts.append(ingest_paths([p]))
    return "\n".join(parts)
