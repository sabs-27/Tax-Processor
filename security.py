"""
Security helpers: sanitize filenames, check allowed file types and sizes, and mask PII in returned JSON.
"""
import re
import os
from typing import Dict, Any

ALLOWED_EXT = {'.pdf', '.txt', '.png', '.jpg', '.jpeg'}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB per file


def sanitize_filename(name: str) -> str:
    # remove path components and dangerous chars
    base = os.path.basename(name)
    # keep alphanumerics, dot, dash, underscore
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', base)
    return safe[:200]


def allowed_file(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_EXT


def mask_ssn_in_text(s: str) -> str:
    # mask SSNs like 123-45-6789 -> XXX-XX-6789
    if not s:
        return s
    return re.sub(r"\b(\d{3})-(\d{2})-(\d{4})\b", r"XXX-XX-\3", s)


def mask_pii_in_result(result: Dict[str, Any]) -> Dict[str, Any]:
    # shallow mask for common keys and any string values
    masked = {}
    for k, v in result.items():
        if isinstance(v, str):
            masked[k] = mask_ssn_in_text(v)
        elif isinstance(v, dict):
            masked[k] = mask_pii_in_result(v)
        elif isinstance(v, list):
            new_list = []
            for item in v:
                if isinstance(item, str):
                    new_list.append(mask_ssn_in_text(item))
                elif isinstance(item, dict):
                    new_list.append(mask_pii_in_result(item))
                else:
                    new_list.append(item)
            masked[k] = new_list
        else:
            masked[k] = v
    return masked
