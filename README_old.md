# Parsing & Extraction demo

This small module demonstrates steps from the project diagram: classify document type (W-2 vs 1099), extract template fields from OCR text, and validate fields.

Files created:
- `parsing/classifier.py` - heuristic classification
- `parsing/parser.py` - regex-based extraction
- `parsing/validator.py` - basic validation rules
- `cli.py` - simple command-line runner reading a text file (simulated OCR)
- `samples/sample_w2.txt` - sample OCR text used by tests
- `tests/test_pipeline.py` - pytest tests

How to run tests (Windows PowerShell):

```powershell
cd C:\Rosy
python -m pip install -r requirements.txt
python -m pytest -q
```

How to try the CLI on the sample file:

```powershell
cd C:\Rosy
python cli.py samples\sample_w2.txt
```

Notes:
- This is a small, local prototype. Replace the text input with OCR output (Tesseract or cloud OCR) to use on real images.
- Parsers use simple heuristics and regexes; expand them with templates or ML models for production.
