"""
Ingestion helpers: read input image(s) or text files and return text to be processed.
This module uses pytesseract if available to OCR images; otherwise it treats files ending with .txt as OCR output.
"""
import os
from typing import List


def read_text_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def ingest_paths(paths: List[str]) -> str:
    """Given a list of file paths (images or text), return combined OCR/text content.
    - PDF files: attempts text extraction first
    - Text files (.txt): read directly
    - Image files: requires Pillow + pytesseract for OCR
    """
    texts = []
    # lazy imports
    has_pil = False
    has_tesseract = False
    has_pdf_tools = False
    
    try:
        from PIL import Image
        has_pil = True
    except Exception:
        Image = None
    try:
        import pytesseract
        has_tesseract = True
    except Exception:
        pytesseract = None
    try:
        from pdf_reader import extract_text_from_pdf
        has_pdf_tools = True
    except Exception:
        extract_text_from_pdf = None

    for p in paths:
        p = os.path.abspath(p)
        ext = os.path.splitext(p)[1].lower()
        
        if ext == '.txt':
            texts.append(read_text_file(p))
        elif ext == '.pdf':
            if has_pdf_tools:
                try:
                    pdf_text = extract_text_from_pdf(p)
                    texts.append(pdf_text)
                except Exception as e:
                    raise RuntimeError(f'Failed to extract text from PDF {p}: {e}')
            else:
                raise RuntimeError('PDF processing requires pdf_reader module')
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            if has_pil and has_tesseract:
                try:
                    img = Image.open(p)
                    txt = pytesseract.image_to_string(img)
                    texts.append(txt)
                except Exception as e:
                    if 'tesseract is not installed' in str(e).lower():
                        raise RuntimeError(
                            'Tesseract OCR is not installed. Please install it:\n'
                            '1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n'
                            '2. Add to PATH or install via: pip install pytesseract\n'
                            '3. For Windows: Also install Tesseract executable\n'
                            'Alternative: Use PDF files with embedded text instead of images'
                        )
                    else:
                        raise RuntimeError(f'OCR failed for {p}: {e}')
            else:
                missing = []
                if not has_pil:
                    missing.append('Pillow (pip install Pillow)')
                if not has_tesseract:
                    missing.append('pytesseract (pip install pytesseract)')
                raise RuntimeError(
                    f'OCR for images requires: {", ".join(missing)}\n'
                    'Alternative: Use PDF files or convert images to text first'
                )
        else:
            raise RuntimeError(f'Unsupported file type: {ext}. Supported: .txt, .pdf, .png, .jpg, .jpeg, .tiff, .bmp, .gif')
    
    return "\n".join(texts)
