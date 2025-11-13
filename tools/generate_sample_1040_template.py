"""
Generate a synthetic fillable Form 1040-like PDF for local testing.
This creates AcroForm text fields with common 1040-like names so the auto-mapper
and form-filling code have a sample template to work with.

Run from repo root:
 python .\tools\generate_sample_1040_template.py

Output: c:\Rosy\templates\1040_fillable.pdf
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, '1040_fillable.pdf')

c = canvas.Canvas(out_path, pagesize=letter)
width, height = letter
c.setFont('Helvetica-Bold', 16)
c.drawString(72, height - 72, 'Sample Fillable Form 1040 (Synthetic)')

# Common 1040 field names to include
fields = [
    ('YourFirstName', 'First name'),
    ('YourLastName', 'Last name'),
    ('SSN', 'SSN'),
    ('Wages', 'Wages, Form W-2 Box 1'),
    ('FederalIncomeTaxWithheld', 'Federal income tax withheld'),
    ('AdjustedGrossIncome', 'Adjusted gross income'),
    ('TaxableIncome', 'Taxable income'),
    ('TotalTax', 'Total tax'),
    ('TotalPayments', 'Total payments'),
    ('TaxDue', 'Amount you owe/refund'),
    ('FilingStatus', 'Filing status'),
    ('EmployerEIN', 'Employer EIN'),
]

# Place fields in two columns
x_label = 72
x_field = 250
y = height - 110
field_h = 18
for i, (name, label) in enumerate(fields):
    col = i % 2
    if col == 0 and i != 0:
        y -= 36
    x_l = x_label if col == 0 else x_label + 260
    x_f = x_field if col == 0 else x_field + 260
    c.setFont('Helvetica', 10)
    c.drawString(x_l, y + 2, label + ':')
    # create a text field
    c.acroForm.textfield(name=name, tooltip=label, x=x_f, y=y, width=200, height=field_h,
                         borderStyle='underlined', forceBorder=True)

# Add a few numeric-looking fields lower
y -= 60
c.setFont('Helvetica-Bold', 12)
c.drawString(72, y, 'Summary')
y -= 22
summary_fields = [
    ('Summary_AGI', 'AGI'),
    ('Summary_TaxableIncome', 'Taxable Income'),
    ('Summary_TotalTax', 'Total Tax'),
]
for name, label in summary_fields:
    c.setFont('Helvetica', 10)
    c.drawString(72, y, label + ':')
    c.acroForm.textfield(name=name, tooltip=label, x=180, y=y-2, width=160, height=field_h,
                         borderStyle='underlined', forceBorder=True)
    y -= 22

c.save()
print('Wrote sample template to', out_path)
