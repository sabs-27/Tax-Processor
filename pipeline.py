"""
Orchestration pipeline tying ingestion -> classification -> extraction -> validation -> tax calc -> form generation.
Provides a function `run_pipeline_on_paths` that accepts file paths (text or images) and an output directory.
"""
import os
from typing import List
from parsing import detect_document_type, extract_fields, validate_fields
from ingestion import ingest_paths
from taxcalc import compute_tax_estimate
from forms import generate_1040_draft


def parse_paths(paths: List[str]) -> List[dict]:
    """Parse each path individually and return a list of per-file parse results.
    Each result contains: path, doc_type, confidence, fields, field_confidence_map, validation_issues.
    """
    results = []
    for p in paths:
        # ingest single path to get its text (supports images/txt/pdf via ingestion)
        txt = ingest_paths([p])
        doc_type, conf = detect_document_type(txt)
        fields = extract_fields(txt, doc_type)
        issues = validate_fields(fields, doc_type)
        # assign a simple confidence per field (placeholder for real confidence)
        field_conf = {k: 0.9 for k in fields.keys()}
        results.append({
            'path': p,
            'doc_type': doc_type,
            'confidence': conf,
            'fields': fields,
            'field_confidence': field_conf,
            'validation_issues': issues,
        })
    return results


def run_pipeline_on_paths(paths: List[str], out_dir: str, *, filing_status: str = 'single', withholding: float = 0.0) -> dict:
    """Full pipeline: parse each file, aggregate incomes and withholdings, compute tax, generate PDF.
    Returns aggregated result and path to generated draft PDF.
    """
    per_file = parse_paths(paths)

    # legacy: also provide a single-document view by concatenating text (backwards compatibility)
    combined_text = ingest_paths(paths)
    legacy_doc_type, legacy_conf = detect_document_type(combined_text)
    legacy_fields = extract_fields(combined_text, legacy_doc_type)
    legacy_issues = validate_fields(legacy_fields, legacy_doc_type)

    # aggregate fields across files
    agg_fields = {}
    total_wages = 0.0
    total_withholding = 0.0
    for r in per_file:
        f = r.get('fields', {})
        # wages/amount
        try:
            if 'wages' in f:
                total_wages += float(str(f['wages']).replace(',', '').replace('$', ''))
            if 'amount' in f:
                total_wages += float(str(f['amount']).replace(',', '').replace('$', ''))
        except Exception:
            pass
        # federal withholding
        try:
            w = f.get('federal_income_tax_withheld') or f.get('federal income tax withheld')
            if w:
                total_withholding += float(str(w).replace(',', '').replace('$', ''))
        except Exception:
            pass

    if total_wages:
        agg_fields['wages'] = round(total_wages, 2)
    if total_withholding:
        agg_fields['withholding'] = round(total_withholding, 2)

    # allow explicit withholding param to override aggregated withholding
    withholding_val = withholding if withholding else total_withholding

    tax = compute_tax_estimate(agg_fields, filing_status=filing_status, withholding=withholding_val)
    form_path = generate_1040_draft(agg_fields, tax, out_dir)

    result = {
        'doc_type': legacy_doc_type,
        'confidence': legacy_conf,
        'fields': legacy_fields,
        'validation_issues': legacy_issues,
        'per_file': per_file,
        'aggregated_fields': agg_fields,
        'tax_estimate': tax,
        'draft_form': form_path,
    }
    return result


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: python pipeline.py out_dir input1.txt [input2.txt ...]')
        sys.exit(2)
    out = sys.argv[1]
    paths = sys.argv[2:]
    res = run_pipeline_on_paths(paths, out)
    print('Pipeline result:')
    print(res)
