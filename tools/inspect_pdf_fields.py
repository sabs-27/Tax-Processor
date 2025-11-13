"""
Inspect AcroForm field names in a PDF and optionally write them to a JSON file.
Usage:
  python tools\inspect_pdf_fields.py path\to\pdf [--out path\to\out.json]

Requires: pdfrw (already in requirements)
"""
import sys
import json
import argparse
from pdfrw import PdfReader


def collect_field_names(field, out):
    """Recursively collect field names from an AcroForm field or kid"""
    if field is None:
        return
    name = field.get('/T')
    if name:
        # pdfrw returns PdfName or PdfString; convert to string
        try:
            out.append(str(name))
        except Exception:
            out.append(name)
    kids = field.get('/Kids')
    if kids:
        for k in kids:
            collect_field_names(k, out)


def inspect(path):
    pdf = PdfReader(path)
    names = []
    try:
        acro = pdf.Root.AcroForm
    except Exception:
        acro = None
    if acro and acro.Fields:
        for f in acro.Fields:
            collect_field_names(f, names)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for n in names:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def main():
    p = argparse.ArgumentParser()
    p.add_argument('pdf')
    p.add_argument('--out', '-o', help='optional output JSON file')
    args = p.parse_args()
    names = inspect(args.pdf)
    if not names:
        print('No AcroForm fields found or the PDF is not a fillable form.')
    else:
        print(f'Found {len(names)} field(s):')
        for n in names:
            print(' -', n)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(names, f, indent=2)
        print(f'Wrote field list to {args.out}')

if __name__ == '__main__':
    main()
