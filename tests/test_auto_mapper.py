from utils.auto_mapper import map_fields


def test_auto_mapper_fallback():
    parsed = {
        'wages': 55000,
        'withholding': 5000,
        'agi': 52000,
        'taxable_income': 48000,
        'tax_due': 2000,
    }
    template_names = [
        'FormWages',
        'FederalIncomeTaxWithheld',
        'AdjustedGrossIncome',
        'TaxableIncome',
        'TotalTax',
    ]

    mapped = map_fields(parsed, template_names)
    # Expect keys for each template and non-none values for at least wages and withholding
    assert isinstance(mapped, dict)
    assert 'FormWages' in mapped
    assert 'FederalIncomeTaxWithheld' in mapped
    # Check that returned tuple is (value, score) or similar
    val, score = mapped['FormWages']
    assert val in (55000,)
    assert 0.0 <= score <= 1.0
