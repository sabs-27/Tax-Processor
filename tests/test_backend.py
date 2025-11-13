import io
import os
from backend import app


def test_upload_text_file(tmp_path):
    client = app.test_client()
    sample = os.path.join(os.path.dirname(__file__), '..', 'samples', 'sample_w2.txt')
    with open(sample, 'rb') as f:
        data = {
            'files': (io.BytesIO(f.read()), 'sample_w2.txt')
        }
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    j = resp.get_json()
    assert 'doc_type' in j
    assert j['doc_type'] == 'W-2'
