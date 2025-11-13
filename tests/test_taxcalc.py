from taxcalc import compute_tax_estimate


def test_taxcalc_basic_single():
    fields = {'wages': '50000'}
    res = compute_tax_estimate(fields, filing_status='single', withholding=5000)
    assert res['agi'] == 50000.0
    assert res['standard_deduction'] == 13850.0
    assert res['taxable_income'] == round(50000 - 13850, 2)
    assert 'gross_tax' in res
    # tax_due = gross_tax - withholding
    assert res['withholding'] == 5000.0


def test_taxcalc_married():
    fields = {'wages': '120000'}
    res = compute_tax_estimate(fields, filing_status='married', withholding=15000)
    assert res['filing_status'] == 'married'
    assert res['agi'] == 120000.0
    assert res['standard_deduction'] == 27700.0
    assert res['taxable_income'] == round(120000 - 27700, 2)
