const form = document.getElementById('upload-form');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  statusEl.textContent = 'Preparing upload...';
  resultEl.innerHTML = '';
  const filesInput = document.getElementById('files');
  const filing_status = document.getElementById('filing_status').value;
  const withholding = document.getElementById('withholding').value || '0';
  if (!filesInput.files.length) {
    statusEl.textContent = 'Please select one or more files to upload.';
    return;
  }
  const fd = new FormData();
  for (const f of filesInput.files) fd.append('files', f, f.name);
  fd.append('filing_status', filing_status);
  fd.append('withholding', withholding);

  statusEl.textContent = 'Uploading...';
  try {
    const resp = await fetch('/upload', { method: 'POST', body: fd });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ error: 'server error' }));
      statusEl.textContent = 'Upload failed: ' + (err.error || resp.statusText);
      return;
    }
    statusEl.textContent = 'Processing complete';
    const j = await resp.json();
    renderResult(j);
  } catch (e) {
    statusEl.textContent = 'Network error: ' + e.message;
  }
});

function renderResult(j) {
  resultEl.innerHTML = '';
  const h = document.createElement('div');
  h.innerHTML = `<h2>Result</h2>
    <p>Detected: ${j.doc_type} (confidence: ${j.confidence})</p>`;
  resultEl.appendChild(h);

  const fields = document.createElement('pre');
  fields.textContent = JSON.stringify(j.fields || {}, null, 2);
  resultEl.appendChild(fields);

  const tax = document.createElement('pre');
  tax.textContent = JSON.stringify(j.tax_estimate || {}, null, 2);
  resultEl.appendChild(tax);

  // If server returned per-file parsing results, show review UI
  if (j.per_file) {
    const review = document.createElement('div');
    review.innerHTML = '<h3>Per-file parsing (review & edit)</h3>';
    j.per_file.forEach((pf, idx) => {
      const box = document.createElement('div');
      box.style.border = '1px solid #ddd';
      box.style.padding = '8px';
      box.style.margin = '6px 0';
      const title = document.createElement('div');
      title.innerHTML = `<strong>File ${idx+1}:</strong> ${pf.path} — ${pf.doc_type} (conf ${pf.confidence})`;
      box.appendChild(title);
      const form = document.createElement('form');
      form.dataset.index = idx;
      for (const [k, v] of Object.entries(pf.fields || {})) {
        const label = document.createElement('label');
        label.style.display = 'block';
        label.textContent = k + ':';
        const inp = document.createElement('input');
        inp.name = k;
        inp.value = v;
        inp.style.width = '60%';
        label.appendChild(inp);
        form.appendChild(label);
      }
      // add save button to update aggregated preview
      const saveBtn = document.createElement('button');
      saveBtn.type = 'button';
      saveBtn.textContent = 'Save changes';
      saveBtn.addEventListener('click', (ev) => {
        // collect fields from form and update displayed aggregated fields
        const els = form.querySelectorAll('input');
        els.forEach(e => { pf.fields[e.name] = e.value; });
        statusEl.textContent = 'Updated fields for ' + pf.path;
        renderAggregated(j);
      });
      form.appendChild(saveBtn);
      box.appendChild(form);
      review.appendChild(box);
    });
    resultEl.appendChild(review);
  }

  // aggregated preview and finalization
  function renderAggregated(j) {
    const ag = document.createElement('div');
    ag.innerHTML = '<h3>Aggregated Preview</h3>';
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(j.aggregated_fields || {}, null, 2);
    ag.appendChild(pre);
    const taxPreview = document.createElement('pre');
    taxPreview.textContent = JSON.stringify(j.tax_estimate || {}, null, 2);
    ag.appendChild(taxPreview);
    const finalize = document.createElement('button');
    finalize.textContent = 'Finalize & Download PDF';
    finalize.addEventListener('click', async () => {
      statusEl.textContent = 'Generating final PDF...';
      // send finalize request to backend with edited per-file fields
      const payload = { per_file: j.per_file, filing_status: document.getElementById('filing_status').value };
      const resp = await fetch('/finalize', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!resp.ok) { statusEl.textContent = 'Finalize failed'; return; }
      // expect PDF bytes back; convert to blob and offer download
      try {
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'draft_1040.pdf';
        link.textContent = 'Download final PDF';
        link.target = '_blank';
        ag.appendChild(link);
        statusEl.textContent = 'Final PDF ready';
      } catch (err) {
        statusEl.textContent = 'Failed to retrieve PDF: ' + err.message;
      }
    });
    ag.appendChild(finalize);
    // replace any previous aggregated area
    const existing = document.getElementById('aggregated-area');
    if (existing) existing.remove();
    ag.id = 'aggregated-area';
    resultEl.appendChild(ag);
  }

  // initial aggregated render if present
  if (j.aggregated_fields) renderAggregated(j);
}
