import os
from pipeline import run_pipeline_on_paths


def test_full_pipeline_creates_draft(tmp_path):
    here = os.path.dirname(__file__)
    sample = os.path.join(here, '..', 'samples', 'sample_w2.txt')
    out_dir = str(tmp_path)
    # pass filing status and withholding as an example
    res = run_pipeline_on_paths([sample], out_dir, filing_status='single', withholding=5000.0)
    assert res['doc_type'] == 'W-2'
    assert 'wages' in res['fields']
    assert 'tax_estimate' in res
    draft = res['draft_form']
    assert os.path.exists(draft)
    # check tax value is numeric and > 0 for sample wages
    assert 'tax_due' in res['tax_estimate']
