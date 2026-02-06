import os
from flask import Flask, request, jsonify, send_file
from markupsafe import escape
from io import BytesIO

from .storage.git_adapter import GitAdapter
from .storage.errors import Conflict

app = Flask(__name__)

# configure storage root relative to repo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STORAGE_ROOT = os.path.join(BASE_DIR, 'data', 'storage')
os.makedirs(STORAGE_ROOT, exist_ok=True)

storage = GitAdapter(STORAGE_ROOT)


@app.route('/upload', methods=['POST'])
def upload():
    # Expect form fields: patient_id, user_id, action, file
    patient_id = request.form.get('patient_id')
    user_id = request.form.get('user_id', 'anonymous')
    action = request.form.get('action', 'upload')
    f = request.files.get('file')
    parent = request.form.get('parent')
    if not patient_id or not f:
        return jsonify({'error': 'patient_id and file are required'}), 400

    filename = f.filename
    relative_path = os.path.join(patient_id, filename)
    data = f.read()
    try:
        commit = storage.save_with_parent(relative_path, data, user_id=user_id, action=action, parent=parent)
    except Conflict as e:
        # handled by errorhandler, but return structure for clarity
        return jsonify({'error': str(e)}), 409

    current_head = storage.head(relative_path)
    return jsonify({'status': 'ok', 'commit': commit, 'head': current_head})


@app.route('/history/<patient_id>/<path:filename>', methods=['GET'])
def history(patient_id, filename):
    relative_path = os.path.join(patient_id, filename)
    h = storage.history(relative_path)
    return jsonify(h)


@app.route('/file/<patient_id>/<path:filename>', methods=['GET'])
def get_file(patient_id, filename):
    version = request.args.get('version')
    relative_path = os.path.join(patient_id, filename)
    data = storage.get(relative_path, version=version)
    return send_file(BytesIO(data), download_name=filename)


@app.route('/diff/<patient_id>/<path:filename>', methods=['GET'])
def diff_versions(patient_id, filename):
    """Return a unified diff between two versions. Query args: a, b (commit hexshas). If b omitted, compare a..HEAD."""
    a = request.args.get('a')
    b = request.args.get('b')
    relative_path = os.path.join(patient_id, filename)
    # use repo git diff
    parts = relative_path.split(os.sep)
    repo = storage._ensure_repo(parts[0])
    rel = os.path.join(*parts[1:])
    if not a and not b:
        return jsonify({'error': 'provide at least one of a or b'}), 400
    # if only a provided, compare a..HEAD
    if a and not b:
        range_spec = f"{a}..HEAD"
    elif a and b:
        range_spec = f"{a}..{b}"
    else:
        # only b provided -> HEAD..b
        range_spec = f"HEAD..{b}"

    try:
        diff_text = repo.git.diff(range_spec, '--', rel)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return (diff_text, 200, {'Content-Type': 'text/plain; charset=utf-8'})


@app.errorhandler(Conflict)
def handle_conflict(e):
    return jsonify({'error': str(e)}), 409


@app.route('/admin/history/<patient_id>/<path:filename>', methods=['GET'])
def admin_history(patient_id, filename):
    """Simple admin HTML view listing commits for a file with links to diffs."""
    relative_path = os.path.join(patient_id, filename)
    h = storage.history(relative_path)
    rows = []
    for item in h:
        rows.append(f"<li><strong>{escape(item['datetime'])}</strong> - {escape(item['author'])} - {escape(item['message'])} - <a href='/admin/diff/{patient_id}/{filename}?a={item['hexsha']}'>diff from here to HEAD</a></li>")
    body = "<h1>History for " + escape(filename) + "</h1><ul>" + "".join(rows) + "</ul>"
    return body


@app.route('/admin/diff/<patient_id>/<path:filename>', methods=['GET'])
def admin_diff(patient_id, filename):
    # wrapper around diff_versions that returns HTML
    a = request.args.get('a')
    b = request.args.get('b')
    rv = diff_versions(patient_id, filename)
    if isinstance(rv, tuple):
        text = rv[0]
    else:
        text = rv
    html = f"<pre>{escape(text)}</pre>"
    return html


if __name__ == '__main__':
    app.run(port=5000, debug=True)
