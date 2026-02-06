"""Simple demo script that runs an end-to-end flow against the Flask app
using the app test client. It uploads an initial file, updates it using
the parent commit, fetches history, and prints a diff.
"""
import tempfile
import io
import json
import sys
import os

# Ensure repo root is on path so imports find the `bhv` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bhv import app as appmod


def run_demo():
    tmp = tempfile.mkdtemp()
    # replace storage with a GitAdapter instance backed by tmp
    from bhv.storage.git_adapter import GitAdapter
    appmod.storage = GitAdapter(tmp)

    client = appmod.app.test_client()

    print('Uploading initial file...')
    data = {
        'patient_id': 'demoPatient',
        'user_id': 'sw001',
        'action': 'initial-upload',
        'file': (io.BytesIO(b'initial content'), 'note.txt')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    print('Status:', resp.status_code)
    print(resp.get_json())
    j = resp.get_json()
    head1 = j.get('head')

    print('\nUploading edited file with parent=head1...')
    data2 = {
        'patient_id': 'demoPatient',
        'user_id': 'sw002',
        'action': 'edit',
        'parent': head1,
        'file': (io.BytesIO(b'updated content'), 'note.txt')
    }
    resp2 = client.post('/upload', data=data2, content_type='multipart/form-data')
    print('Status:', resp2.status_code)
    print(resp2.get_json())

    print('\nFetching history...')
    resp3 = client.get('/history/demoPatient/note.txt')
    print('Status:', resp3.status_code)
    print(json.dumps(resp3.get_json(), indent=2))

    # get diff between first commit and HEAD
    commits = resp3.get_json()
    if commits and len(commits) >= 2:
        a = commits[0]['hexsha']
        print(f"\nDiff from {a} to HEAD:")
        respd = client.get(f'/diff/demoPatient/note.txt?a={a}')
        print(respd.get_data(as_text=True))


if __name__ == '__main__':
    run_demo()
