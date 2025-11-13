"""
Simple form generator: produce a draft '1040' text file using parsed fields and tax results.
This is a placeholder for PDF form-filling.
"""
import os
from typing import Dict, Any, List
import io

# local auto-mapper (optional heavy dependency handled inside)
from utils.auto_mapper import map_fields


def format_currency(value) -> str:
    """Format a numeric value as currency string."""
    if value is None:
        return ""
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def create_exact_field_map(fields: Dict[str, Any], tax_result: Dict[str, Any]) -> Dict[str, str]:
    """Create exact mapping for the synthetic 1040 template fields."""
    field_map = {}
    
    # Personal info
    field_map['YourFirstName'] = fields.get('first_name', '')
    field_map['YourLastName'] = fields.get('last_name', '')
    field_map['SSN'] = fields.get('ssn', '')
    field_map['FilingStatus'] = fields.get('filing_status', 'Single')
    field_map['EmployerEIN'] = fields.get('ein', '')
    
    # Income and withholding
    field_map['Wages'] = format_currency(fields.get('wages'))
    field_map['FederalIncomeTaxWithheld'] = format_currency(fields.get('withholding'))
    
    # Tax calculations
    field_map['AdjustedGrossIncome'] = format_currency(tax_result.get('agi'))
    field_map['TaxableIncome'] = format_currency(tax_result.get('taxable_income'))
    field_map['TotalTax'] = format_currency(tax_result.get('gross_tax'))
    field_map['TotalPayments'] = format_currency(tax_result.get('withholding'))
    field_map['TaxDue'] = format_currency(tax_result.get('tax_due'))
    
    # Summary fields (duplicates for template layout)
    field_map['Summary_AGI'] = format_currency(tax_result.get('agi'))
    field_map['Summary_TaxableIncome'] = format_currency(tax_result.get('taxable_income'))
    field_map['Summary_TotalTax'] = format_currency(tax_result.get('gross_tax'))
    
    return field_map


def _generate_text_draft(fields: Dict[str, Any], tax_result: Dict[str, Any], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'draft_1040.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('DRAFT Form 1040\n')
        f.write('================\n\n')
        f.write('Extracted fields:\n')
        for k, v in fields.items():
            f.write(f'  {k}: {v}\n')
        f.write('\nTax estimate:\n')
        for k, v in tax_result.items():
            f.write(f'  {k}: {v}\n')
        f.write('\nNotes: This is an auto-generated draft. Review all fields carefully.\n')
    return out_path


def generate_1040_pdf(fields: Dict[str, Any], tax_result: Dict[str, Any], out_dir: str) -> str:
    """Generate a simple two-page PDF: page1 contains extracted fields, page2 contains tax summary.
    Uses reportlab if available; otherwise falls back to text draft.
    Returns the path to the generated file.
    """
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'draft_1040.pdf')
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        # fallback
        return _generate_text_draft(fields, tax_result, out_dir)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    # page 1: header + fields
    c.setFont('Helvetica-Bold', 14)
    c.drawString(72, height - 72, 'DRAFT Form 1040')
    c.setFont('Helvetica', 10)
    y = height - 100
    c.drawString(72, y, 'Extracted fields:')
    y -= 16
    for k, v in fields.items():
        c.drawString(80, y, f'{k}: {v}')
        y -= 14
        if y < 72:
            c.showPage()
            y = height - 72

    c.showPage()
    # page 2: tax summary
    c.setFont('Helvetica-Bold', 12)
    c.drawString(72, height - 72, 'Tax Estimate Summary')
    c.setFont('Helvetica', 10)
    y = height - 100
    for k, v in tax_result.items():
        c.drawString(80, y, f'{k}: {v}')
        y -= 14
        if y < 72:
            c.showPage()
            y = height - 72

    c.showPage()
    c.save()
    return pdf_path

def fill_fillable_1040(template_path: str, field_values: Dict[str, Any], out_path: str) -> str:
    """Fill a fillable PDF template using pdfrw. `field_values` maps template field names to values.
    Returns the path to the filled PDF. If pdfrw isn't available or the template is missing, raises RuntimeError.
    """
    try:
        from pdfrw import PdfReader, PdfWriter, PdfDict
    except Exception:
        raise RuntimeError('pdfrw is required to fill a fillable PDF')

    if not os.path.exists(template_path):
        raise RuntimeError('template not found: ' + template_path)

    pdf = PdfReader(template_path)

    # AcroForm fields may be found under pdf.Root.AcroForm.Fields
    # We'll iterate annotations and set /V for matching /T names.
    for page in pdf.pages:
        annotations = page.Annots
        if annotations is None:
            continue
        for annot in annotations:
            if annot.Subtype and annot.Subtype == '/Widget' and annot.T:
                name = annot.T.to_unicode() if hasattr(annot.T, 'to_unicode') else str(annot.T)
                # pdfrw stores names like (FieldName)
                if name.startswith('(') and name.endswith(')'):
                    name = name[1:-1]
                if name in field_values:
                    val = str(field_values[name])
                    annot.V = '(%s)' % val
                    annot.AP = None

    # ensure AcroForm /NeedAppearances is set so PDF viewers regenerate appearances
    if pdf.Root is None:
        pdf.Root = PdfDict()
    if pdf.Root.AcroForm is None:
        pdf.Root.AcroForm = PdfDict()
    pdf.Root.AcroForm.update(PdfDict(NeedAppearances=True))

    PdfWriter().write(out_path, pdf)
    return out_path


def generate_1040_draft(fields: Dict[str, Any], tax_result: Dict[str, Any], out_dir: str) -> str:
    """Main entry: try PDF generation and return generated path (PDF preferred, fallback to text)."""
    # Prefer to fill a real fillable 1040 if a template is present
    here = os.path.dirname(__file__)
    template_path = os.path.join(here, '..', 'templates', '1040_fillable.pdf')
    os.makedirs(out_dir, exist_ok=True)
    try:
        if os.path.exists(template_path):
            # Read template field names (AcroForm) and attempt an automatic mapping
            try:
                from pdfrw import PdfReader

                def _collect_fields(obj, out: List[str]):
                    if obj is None:
                        return
                    # obj may be a PdfDict with /T or have /Kids
                    try:
                        if getattr(obj, 'T', None):
                            name = obj.T
                            try:
                                name = name.to_unicode()
                            except Exception:
                                name = str(name)
                            if name.startswith('(') and name.endswith(')'):
                                name = name[1:-1]
                            out.append(name)
                    except Exception:
                        pass
                    kids = getattr(obj, 'Kids', None) or getattr(obj, 'Fields', None)
                    if kids:
                        for k in kids:
                            _collect_fields(k, out)

                pdf = PdfReader(template_path)
                acro = getattr(getattr(pdf, 'Root', None), 'AcroForm', None)
                names: List[str] = []
                if acro and getattr(acro, 'Fields', None):
                    for f in acro.Fields:
                        _collect_fields(f, names)
                # dedupe
                seen = set()
                uniq = []
                for n in names:
                    if n not in seen:
                        seen.add(n)
                        uniq.append(n)
                template_field_names = uniq
            except Exception:
                template_field_names = []

            # Use exact field mapping if this is our synthetic template
            mapping = create_exact_field_map(fields, tax_result)
            
            # If mapping is incomplete, try auto-mapper as fallback
            if len([v for v in mapping.values() if v]) < 5:  # Less than 5 non-empty values
                # Build a combined parsed dict that includes tax_result values with readable keys
                parsed_combined: Dict[str, Any] = {}
                parsed_combined.update(fields)
                # add common tax_result keys with friendly labels
                for k, v in tax_result.items():
                    parsed_combined[k] = v

                # map parsed fields to template field names using the auto-mapper
                auto_mapping = {}
                try:
                    mapped = map_fields(parsed_combined, template_field_names)
                    # Only include mappings with some minimal confidence
                    for tname, (val, score) in mapped.items():
                        if val is None:
                            continue
                        # threshold: accept if score >= 0.4 (fallback) or higher for embeddings
                        if score and score >= 0.4:
                            auto_mapping[tname] = val
                except Exception:
                    auto_mapping = {}
                
                # Merge auto-mapping for missing fields
                for k, v in auto_mapping.items():
                    if not mapping.get(k):
                        mapping[k] = v

            out_path = os.path.join(out_dir, 'draft_1040_filled.pdf')
            try:
                return fill_fillable_1040(template_path, mapping, out_path)
            except Exception:
                # fall back to reportlab-based draft
                return generate_1040_pdf(fields, tax_result, out_dir)
        else:
            return generate_1040_pdf(fields, tax_result, out_dir)
    finally:
        pass
