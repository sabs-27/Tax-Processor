"""
Field validation: required presence and basic numeric sanity checks.
Returns a list of issues (empty if OK).
"""
from typing import Dict, Any, List


def _to_float(s: str):
    if s is None: return None
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return None


def validate_fields(fields: Dict[str, Any], doc_type: str) -> List[str]:
    issues: List[str] = []
    if doc_type == 'W-2':
        # required: wages and employee_ssn (at least wages)
        if 'wages' not in fields:
            issues.append('missing wages (Box 1)')
        else:
            val = _to_float(fields.get('wages'))
            if val is None:
                issues.append('wages not parseable as number')
            else:
                if val < 0:
                    issues.append('wages negative')
                if val > 10_000_000:
                    issues.append('wages unusually large')
        # EIN optional but warn if malformed
        ein = fields.get('ein')
        if ein and not isinstance(ein, str):
            issues.append('ein not a string')

    elif doc_type == '1099':
        if 'amount' not in fields:
            issues.append('missing amount (Box 1)')
        else:
            val = _to_float(fields.get('amount'))
            if val is None:
                issues.append('amount not parseable as number')
            else:
                if val < 0:
                    issues.append('amount negative')
        # payer EIN optional
        ein = fields.get('payer_ein')
        if ein and not isinstance(ein, str):
            issues.append('payer_ein not a string')

    else:
        if not fields:
            issues.append('no fields extracted')

    return issues
