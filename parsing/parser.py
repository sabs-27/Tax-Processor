"""
Template-based (heuristic/regex) extraction for common fields from OCR text.
Supports W-2 and 1099 basic fields for demonstration.
"""
import re
from typing import Dict, Any

_number_re = re.compile(r"[-+]?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?")
_ein_re = re.compile(r"\b\d{2}-\d{7}\b")
_ssn_re = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _find_first_number_near(keyword: str, text: str):
    # find keyword and then search numbers in the following 40 characters
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return None
    window = text[idx: idx + 120]
    m = _number_re.search(window)
    if m:
        return m.group(0)
    # fallback: search globally
    m = _number_re.search(text)
    return m.group(0) if m else None


def extract_fields(text: str, doc_type: str) -> Dict[str, Any]:
    text = text or ""
    fields: Dict[str, Any] = {}

    if doc_type == 'W-2':
        # wages - try 'box 1' or 'wages'
        wages = None
        m = re.search(r'box\s*1[:\)]?\s*([^\n\r]+)', text, flags=re.IGNORECASE)
        if m:
            wages = _number_re.search(m.group(1))
            if wages: wages = wages.group(0)
        if not wages:
            wages = _find_first_number_near('wages', text)
        if wages:
            fields['wages'] = wages

        # EIN
        ein = _ein_re.search(text)
        if ein:
            fields['ein'] = ein.group(0)

        # employee SSN
        ssn = _ssn_re.search(text)
        if ssn:
            fields['employee_ssn'] = ssn.group(0)

        # federal income tax withheld (Box 2)
        tax_withheld = _find_first_number_near('box 2', text) or _find_first_number_near('federal income tax withheld', text)
        if tax_withheld:
            fields['federal_income_tax_withheld'] = tax_withheld

    elif doc_type == '1099':
        # payer TIN/EIN
        ein = _ein_re.search(text)
        if ein:
            fields['payer_ein'] = ein.group(0)

        # recipient SSN/TIN
        ssn = _ssn_re.search(text)
        if ssn:
            fields['recipient_ssn'] = ssn.group(0)

        # amount - try 'box 1' or 'nonemployee compensation' or 'amount'
        amt = _find_first_number_near('nonemployee compensation', text) or _find_first_number_near('box 1', text) or _find_first_number_near('amount', text)
        if amt:
            fields['amount'] = amt

    else:
        # generic heuristics
        ein = _ein_re.search(text)
        if ein:
            fields['ein'] = ein.group(0)
        ssn = _ssn_re.search(text)
        if ssn:
            fields['ssn'] = ssn.group(0)

    return fields
