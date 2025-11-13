"""
Simple heuristic classifier for tax forms (W-2 vs 1099).
Returns a tuple (doc_type, confidence) where doc_type is 'W-2', '1099' or 'unknown'.
"""

def detect_document_type(text: str):
    text_lower = (text or "").lower()
    score_w2 = 0
    score_1099 = 0

    # strong signals
    if 'form w-2' in text_lower or '\nw-2' in text_lower or 'w-2 ' in text_lower:
        score_w2 += 3
    if 'form 1099' in text_lower or '1099-' in text_lower or '\n1099' in text_lower:
        score_1099 += 3

    # medium signals
    if 'employer identification number' in text_lower or 'ein' in text_lower:
        score_w2 += 1
    if 'payer' in text_lower and 'recipient' in text_lower:
        score_1099 += 1

    # weak signals
    if 'wages' in text_lower or 'box 1' in text_lower:
        score_w2 += 1
    if 'nonemployee compensation' in text_lower or 'federal income tax withheld' in text_lower:
        # can appear on both, but boost 1099 a bit
        score_1099 += 0.5

    if score_w2 == 0 and score_1099 == 0:
        return ('unknown', 0.0)

    if score_w2 > score_1099:
        conf = float(score_w2) / (score_w2 + score_1099)
        return ('W-2', round(conf, 2))
    elif score_1099 > score_w2:
        conf = float(score_1099) / (score_w2 + score_1099)
        return ('1099', round(conf, 2))
    else:
        # tie -> unknown low confidence
        return ('unknown', 0.5)
