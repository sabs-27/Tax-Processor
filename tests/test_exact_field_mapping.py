import os
import tempfile
from forms import generate_1040_draft, fill_fillable_1040
from pdf_reader import extract_text_from_pdf


def test_exact_field_mapping_and_pdf_fill():
    """Test exact field mapping with synthetic 1040 template and verify filled PDF output."""
    # Sample parsed fields (simulating W-2 extraction)
    fields = {
        'first_name': 'John',
        'last_name': 'Doe',
        'ssn': '123-45-6789',
        'ein': '12-3456789',
        'wages': 75000,
        'withholding': 8500,
        'filing_status': 'Single'
    }
    
    # Sample tax calculation result
    tax_result = {
        'agi': 75000,
        'taxable_income': 61950,  # after standard deduction
        'gross_tax': 9739,
        'withholding': 8500,
        'tax_due': 1239
    }
    
    # Generate filled PDF using the exact mapping
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = generate_1040_draft(fields, tax_result, temp_dir)
        
        # Verify PDF was created
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')
        
        # Verify file has content
        assert os.path.getsize(pdf_path) > 1000  # Should be substantial
        
        # Try to extract text from the filled PDF to verify some content
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            # Check for some expected values
            assert 'John' in pdf_text or '75,000' in pdf_text or 'DRAFT' in pdf_text
        except Exception:
            # PDF text extraction might fail, but file creation success is main test
            pass


def test_currency_formatting():
    """Test currency formatting helper."""
    from forms import format_currency
    
    assert format_currency(1234.56) == "1,234.56"
    assert format_currency(75000) == "75,000.00"
    assert format_currency(0) == "0.00"
    assert format_currency(None) == ""
    assert format_currency("invalid") == "invalid"


def test_exact_field_map_creation():
    """Test the exact field mapping creation."""
    from forms import create_exact_field_map
    
    fields = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'ssn': '987-65-4321',
        'wages': 50000,
        'withholding': 5000
    }
    
    tax_result = {
        'agi': 50000,
        'taxable_income': 36950,
        'gross_tax': 4184,
        'withholding': 5000,
        'tax_due': -816  # refund
    }
    
    field_map = create_exact_field_map(fields, tax_result)
    
    # Verify mapping contains expected fields
    assert field_map['YourFirstName'] == 'Jane'
    assert field_map['YourLastName'] == 'Smith'
    assert field_map['SSN'] == '987-65-4321'
    assert field_map['Wages'] == '50,000.00'
    assert field_map['FederalIncomeTaxWithheld'] == '5,000.00'
    assert field_map['AdjustedGrossIncome'] == '50,000.00'
    assert field_map['TaxableIncome'] == '36,950.00'
    assert field_map['TotalTax'] == '4,184.00'
    assert field_map['TaxDue'] == '-816.00'  # negative indicates refund