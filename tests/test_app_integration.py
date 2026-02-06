import tempfile
import io
import os

from bhv.app import app
from bhv.storage.git_adapter import GitAdapter


def _setup_storage(tmpdir):
    # Replace the app's storage with a GitAdapter backed by tmpdir
    adapter = GitAdapter(tmpdir)
    import bhv.app as appmod
    appmod.storage = adapter
    return adapter


def test_upload_and_history_flow():
    tmp = tempfile.mkdtemp()
    _setup_storage(tmp)
    client = app.test_client()

    # first upload
    data = {
        'patient_id': 'patientX',
        'user_id': 'tester',
        'action': 'narrative',
        'file': (io.BytesIO(b'first version'), 'notes.txt')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    j = resp.get_json()
    assert 'commit' in j
    head1 = j.get('head')

    # second upload using parent=head1
    data2 = {
        'patient_id': 'patientX',
        'user_id': 'tester2',
        'action': 'edit',
        'parent': head1,
        'file': (io.BytesIO(b'second version'), 'notes.txt')
    }
    resp2 = client.post('/upload', data=data2, content_type='multipart/form-data')
    assert resp2.status_code == 200
    j2 = resp2.get_json()
    assert j2.get('commit') != j.get('commit')

    # history should list two commits
    resp3 = client.get('/history/patientX/notes.txt')
    assert resp3.status_code == 200
    hist = resp3.get_json()
    assert isinstance(hist, list) and len(hist) == 2


def test_upload_conflict_returns_409():
    tmp = tempfile.mkdtemp()
    _setup_storage(tmp)
    client = app.test_client()

    # initial upload
    resp = client.post('/upload', data={
        'patient_id': 'p2',
        'user_id': 'u',
        'action': 'create',
        'file': (io.BytesIO(b'a'), 'file.txt')
    }, content_type='multipart/form-data')
    assert resp.status_code == 200

    # attempt save with wrong parent should return 409
    resp2 = client.post('/upload', data={
        'patient_id': 'p2',
        'user_id': 'u2',
        'action': 'edit',
        'parent': 'deadbeef',
        'file': (io.BytesIO(b'b'), 'file.txt')
    }, content_type='multipart/form-data')
    assert resp2.status_code == 409
