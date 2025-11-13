import io
import os
from backend import app


def test_reject_disallowed_file(tmp_path):
    client = app.test_client()
    # create a disallowed file type
    data = {
        'files': (io.BytesIO(b'data'), 'malicious.exe')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert 'disallowed file type' in resp.get_json().get('error', '')


def test_mask_ssn_in_response(tmp_path):
    client = app.test_client()
    sample = os.path.join(os.path.dirname(__file__), '..', 'samples', 'sample_w2.txt')
    # ensure sample contains an SSN (it does)
    with open(sample, 'rb') as f:
        data = {
            'files': (io.BytesIO(f.read()), 'sample_w2.txt')
        }
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    j = resp.get_json()
    # check that any employee_ssn field in fields is masked
    fields = j.get('fields', {})
    ssn = fields.get('employee_ssn')
    if ssn:
        assert ssn.startswith('XXX-XX-')
