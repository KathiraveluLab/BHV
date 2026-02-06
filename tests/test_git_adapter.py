import tempfile
import os
from bhv.storage.git_adapter import GitAdapter


def test_save_and_history():
    # Use mkdtemp and don't attempt automatic cleanup on Windows where
    # GitPython may leave short-lived handles that block removal.
    tmp = tempfile.mkdtemp()
    adapter = GitAdapter(tmp)
    rel = os.path.join('patientA', 'notes.txt')
    commit1 = adapter.save(rel, b'first version', user_id='user1', action='create')
    commit2 = adapter.save(rel, b'second version', user_id='user2', action='edit')

    hist = adapter.history(rel)
    assert len(hist) == 2
    # latest content should be second version
    data = adapter.get(rel)
    assert data == b'second version'

    # retrieve first version by commit hash
    data1 = adapter.get(rel, version=hist[0]['hexsha'])
    assert data1 == b'first version'


def test_save_with_parent_conflict():
    tmp = tempfile.mkdtemp()
    adapter = GitAdapter(tmp)
    rel = os.path.join('patientB', 'notes.txt')
    commit1 = adapter.save(rel, b'one', user_id='u1', action='create')
    # successful save when parent matches
    commit2 = adapter.save_with_parent(rel, b'two', user_id='u2', action='edit', parent=commit1)
    assert commit2 != commit1

    # attempt save with wrong parent should raise
    from bhv.storage.errors import Conflict
    try:
        adapter.save_with_parent(rel, b'three', user_id='u3', action='edit', parent='deadbeef')
        assert False, "Expected conflict"
    except Conflict:
        pass
