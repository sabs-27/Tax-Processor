"""
Simple CLI to run detection -> extraction -> validation on a text file (simulating OCR output).
Usage: python cli.py path/to/textfile.txt
"""
import sys
from parsing import detect_document_type, extract_fields, validate_fields


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py path/to/textfile.txt")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    doc_type, conf = detect_document_type(txt)
    print(f"Detected: {doc_type} (confidence={conf})")
    fields = extract_fields(txt, doc_type)
    print('Extracted fields:')
    for k, v in fields.items():
        print(f'  {k}: {v}')
    issues = validate_fields(fields, doc_type)
    if issues:
        print('\nValidation issues:')
        for it in issues:
            print(f'  - {it}')
    else:
        print('\nValidation: OK')

if __name__ == '__main__':
    main()
