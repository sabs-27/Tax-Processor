Place your fillable Form 1040 PDF in this directory as `1040_fillable.pdf` so the project can use it to fill fields.

To inspect the AcroForm field names (so we can map parsed values to the template), run the inspector script from the repository root.

PowerShell example:

```powershell
# from repository root (c:\Rosy)
python .\tools\inspect_pdf_fields.py .\templates\1040_fillable.pdf -o .\templates\1040_fields.json

# The script will print found field names and optionally write them to the JSON file.
``` 

If the PDF does not contain form fields, the project will fall back to generating a ReportLab draft PDF instead.
