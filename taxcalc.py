"""
Enhanced tax calculator that loads tax brackets from `tax_brackets.json` and supports filing status and withholding.
"""
from typing import Dict, Any, List
import json
import os

# default standard deductions (small demo values)
STANDARD_DEDUCTIONS = {
    'single': 13850.0,
    'married': 27700.0
}


def _load_brackets():
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'tax_brackets.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # fallback to a builtin minimal set
        return {
            'single': [
                {'upto': 11000.0, 'rate': 0.10},
                {'upto': 44725.0, 'rate': 0.12},
                {'upto': 95375.0, 'rate': 0.22},
                {'upto': 182100.0, 'rate': 0.24},
            ],
            'married': [
                {'upto': 22000.0, 'rate': 0.10},
                {'upto': 89450.0, 'rate': 0.12},
                {'upto': 190750.0, 'rate': 0.22},
                {'upto': 364200.0, 'rate': 0.24},
            ]
        }


def _compute_progressive_tax_for_brackets(taxable: float, brackets: List[Dict[str, float]]) -> float:
    tax = 0.0
    lower = 0.0
    for b in brackets:
        upper = float(b['upto'])
        rate = float(b['rate'])
        if taxable <= lower:
            break
        taxable_in_bracket = min(taxable, upper) - lower
        if taxable_in_bracket > 0:
            tax += taxable_in_bracket * rate
        lower = upper
    if taxable > lower:
        # continue at a reasonable top rate for demo
        tax += (taxable - lower) * 0.32
    return tax


def compute_tax_estimate(extracted_fields: Dict[str, Any], *, filing_status: str = 'single', withholding: float = 0.0) -> Dict[str, Any]:
    """Compute a basic tax estimate.

    - `extracted_fields` may include 'wages' or 'amount' or multiple income numbers (as strings).
    - `filing_status` should be 'single' or 'married' (defaults to 'single').
    - `withholding` is the total withholding amount to subtract when computing refund/due.
    Returns dict with AGI, deduction, taxable income, gross tax, withholding, and final tax due (positive means tax due, negative means refund).
    """
    # collect numeric-like fields
    incomes = []
    for key in ('wages', 'amount'):
        if key in extracted_fields:
            try:
                incomes.append(float(str(extracted_fields[key]).replace(',', '').replace('$', '')))
            except Exception:
                pass

    agi = sum(incomes)
    deductions = STANDARD_DEDUCTIONS.get(filing_status, STANDARD_DEDUCTIONS['single'])
    taxable = max(0.0, agi - deductions)

    brackets = _load_brackets().get(filing_status, _load_brackets().get('single'))
    gross_tax = _compute_progressive_tax_for_brackets(taxable, brackets)

    # final: subtract withholding
    tax_after_withholding = gross_tax - float(withholding or 0.0)

    return {
        'filing_status': filing_status,
        'agi': round(agi, 2),
        'standard_deduction': round(deductions, 2),
        'taxable_income': round(taxable, 2),
        'gross_tax': round(gross_tax, 2),
        'withholding': round(float(withholding or 0.0), 2),
        'tax_due': round(tax_after_withholding, 2),
    }
