"""
Simple Flask backend with an upload endpoint that runs the pipeline.
POST /upload expects 'files' in form-data (multiple allowed). Returns JSON with pipeline result.
"""
import os
import tempfile
from flask import Flask, request, jsonify, send_file
from pipeline import run_pipeline_on_paths
from security import sanitize_filename, allowed_file, mask_pii_in_result, MAX_UPLOAD_BYTES
from taxcalc import compute_tax_estimate
from forms import generate_1040_draft

app = Flask(__name__)

# Serve frontend
@app.route('/')
def index():
    root = os.path.join(os.path.dirname(__file__), 'frontend')
    with open(os.path.join(root, 'index.html'), 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/app.js')
def app_js():
    root = os.path.join(os.path.dirname(__file__), 'frontend')
    with open(os.path.join(root, 'app.js'), 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}


@app.route('/static.css')
def static_css():
    root = os.path.join(os.path.dirname(__file__), 'frontend')
    with open(os.path.join(root, 'static.css'), 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}


@app.route('/download')
def download():
    # This is a simple helper for the demo: it reads the file path provided and returns bytes.
    # WARNING: Do NOT use this approach in production (path traversal risk). It's for local demo only.
    path = request.args.get('path')
    if not path or not os.path.exists(path):
        return 'Not found', 404
    # only allow files under temp dirs we create
    # quick check: ensure path contains 'rosy_upload_'
    if 'rosy_upload_' not in path:
        return 'Not allowed', 403
    with open(path, 'rb') as f:
        data = f.read()
    return data, 200, {'Content-Type': 'application/pdf'}

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'no files uploaded'}), 400
    tmpdir = tempfile.mkdtemp(prefix='rosy_upload_')
    paths = []
    for f in files:
        filename = sanitize_filename(f.filename or 'uploaded')
        dest = os.path.join(tmpdir, filename)
        # basic size check if provided by stream
        content = f.read()
        if len(content) > MAX_UPLOAD_BYTES:
            return jsonify({'error': 'file too large'}), 400
        f.stream.seek(0)
        f.save(dest)
        # validate extension
        if not allowed_file(dest):
            return jsonify({'error': f'disallowed file type: {filename}'}), 400
        paths.append(dest)
    out_dir = os.path.join(tmpdir, 'out')
    os.makedirs(out_dir, exist_ok=True)
    # optional form fields for taxpayer info
    filing_status = request.form.get('filing_status', 'single')
    withholding = request.form.get('withholding', '0')
    try:
        withholding_val = float(withholding)
    except Exception:
        withholding_val = 0.0

    try:
        res = run_pipeline_on_paths(paths, out_dir, filing_status=filing_status, withholding=withholding_val)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # mask PII in returned result
    safe = mask_pii_in_result(res)

    # cleanup uploaded files
    try:
        for p in paths:
            os.remove(p)
    except Exception:
        pass

    return jsonify(safe)


@app.route('/finalize', methods=['POST'])
def finalize():
    # Accept edited per-file fields from frontend and regenerate final PDF
    data = request.get_json() or {}
    per_file = data.get('per_file', [])
    filing_status = data.get('filing_status', 'single')
    # create a temporary dir to render final
    tmpdir = tempfile.mkdtemp(prefix='rosy_final_')
    out_dir = os.path.join(tmpdir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    # aggregate fields from provided per_file entries
    agg_fields = {}
    total_wages = 0.0
    total_withholding = 0.0
    for r in per_file:
        f = r.get('fields', {})
        try:
            if 'wages' in f:
                total_wages += float(str(f['wages']).replace(',', '').replace('$', ''))
            if 'amount' in f:
                total_wages += float(str(f['amount']).replace(',', '').replace('$', ''))
        except Exception:
            pass
        try:
            w = f.get('federal_income_tax_withheld') or f.get('federal income tax withheld') or f.get('withholding')
            if w:
                total_withholding += float(str(w).replace(',', '').replace('$', ''))
        except Exception:
            pass

    if total_wages:
        agg_fields['wages'] = round(total_wages, 2)
    if total_withholding:
        agg_fields['withholding'] = round(total_withholding, 2)

    tax = compute_tax_estimate(agg_fields, filing_status=filing_status, withholding=total_withholding)
    form_path = generate_1040_draft(agg_fields, tax, out_dir)
    # Stream the PDF back as an attachment (demo). In production, ensure auth and secure storage.
    try:
        return send_file(form_path, mimetype='application/pdf', as_attachment=True, download_name='draft_1040.pdf')
    except Exception:
        # fallback: return a minimal JSON indicating where the file is (masked)
        res = {'aggregated_fields': agg_fields, 'tax_estimate': tax, 'draft_form': form_path}
        safe = mask_pii_in_result(res)
        return jsonify(safe)

if __name__ == '__main__':
    app.run(port=5000)
