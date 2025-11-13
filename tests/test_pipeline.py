import os
from parsing import detect_document_type, extract_fields, validate_fields


def load_sample(name: str):
    here = os.path.dirname(__file__)
    p = os.path.join(here, '..', 'samples', name)
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def test_detect_w2():
    txt = load_sample('sample_w2.txt')
    doc_type, conf = detect_document_type(txt)
    assert doc_type == 'W-2'
    assert conf > 0.5


def test_extract_and_validate_w2():
    txt = load_sample('sample_w2.txt')
    doc_type, _ = detect_document_type(txt)
    fields = extract_fields(txt, doc_type)
    assert 'wages' in fields
    assert fields['wages'] in ('50,000.00', '50000.00', '50,000.0', '50000') or '50' in fields['wages']
    issues = validate_fields(fields, doc_type)
    assert issues == []
