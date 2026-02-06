import os
import threading
from typing import Optional, List, Dict
from git import Repo, Actor

from .base import StorageAdapter
from .errors import Conflict


class GitAdapter(StorageAdapter):
    """A simple Git-backed storage adapter.

    This adapter stores each patient's vault under a separate directory
    (root_dir/<patient_id>/...). Each save writes the file and creates
    a git commit with metadata in the message.
    """

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)
        self._locks = {}  # patient_id -> threading.Lock

    def _ensure_repo(self, patient_id: str) -> Repo:
        repo_path = os.path.join(self.root_dir, patient_id)
        os.makedirs(repo_path, exist_ok=True)
        if not os.path.exists(os.path.join(repo_path, '.git')):
            Repo.init(repo_path)
        # return a fresh Repo object to avoid long-lived file handles on Windows
        if patient_id not in self._locks:
            self._locks[patient_id] = threading.Lock()
        return Repo(repo_path)

    def save(self, relative_path: str, data: bytes, user_id: str, action: str, message: Optional[str] = None) -> str:
        # relative_path expected: '<patient_id>/path/to/file.ext'
        parts = relative_path.split(os.sep)
        if len(parts) < 2:
            raise ValueError("relative_path must start with '<patient_id>/...'")
        patient_id = parts[0]
        repo = self._ensure_repo(patient_id)
        lock = self._locks[patient_id]
        full_path = os.path.join(repo.working_tree_dir, *parts[1:])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Default save uses no parent check
        return self.save_with_parent(relative_path, data, user_id, action, parent=None, message=message)

    def save_with_parent(self, relative_path: str, data: bytes, user_id: str, action: str, parent: Optional[str] = None, message: Optional[str] = None) -> str:
        parts = relative_path.split(os.sep)
        patient_id = parts[0]
        repo = self._ensure_repo(patient_id)
        lock = self._locks[patient_id]
        full_path = os.path.join(repo.working_tree_dir, *parts[1:])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with lock:
            # optimistic locking: if parent provided, ensure HEAD matches
            try:
                head = repo.head.commit.hexsha
            except Exception:
                head = None

            if parent is not None and parent != head:
                raise Conflict(f"Conflict: expected parent {parent} but head is {head}")

            with open(full_path, 'wb') as f:
                f.write(data)

            repo.index.add([os.path.relpath(full_path, repo.working_tree_dir)])
            actor = Actor("BHV System", "no-reply@example.com")
            commit_message = message or f"{action} by user {user_id} on {relative_path}"
            commit = repo.index.commit(commit_message, author=actor, committer=actor)
            # Ensure HEAD points to a branch that exists. Some environments
            # may have a mismatched HEAD symbolic ref (e.g. refs/heads/main)
            # which can cause later repo.head access to fail. Create a
            # 'main' branch pointing to this commit if necessary and ensure
            # HEAD references it.
            try:
                _ = repo.head.commit.hexsha
            except Exception:
                try:
                    if 'main' not in [h.name for h in repo.heads]:
                        repo.create_head('main', commit)
                    repo.head.reference = repo.heads['main']
                except Exception:
                    # best-effort; if this fails, continue and return commit
                    pass
            return commit.hexsha

    def get(self, relative_path: str, version: Optional[str] = None) -> bytes:
        parts = relative_path.split(os.sep)
        if len(parts) < 2:
            raise ValueError("relative_path must start with '<patient_id>/...'")
        patient_id = parts[0]
        repo = self._ensure_repo(patient_id)
        rel_path = os.path.join(*parts[1:])
        if version is None:
            # read from working tree
            target = os.path.join(repo.working_tree_dir, rel_path)
            with open(target, 'rb') as f:
                return f.read()
        else:
            commit = repo.commit(version)
            blob = commit.tree / rel_path
            return blob.data_stream.read()

    def history(self, relative_path: str) -> List[Dict]:
        parts = relative_path.split(os.sep)
        if len(parts) < 2:
            raise ValueError("relative_path must start with '<patient_id>/...'")
        patient_id = parts[0]
        repo = self._ensure_repo(patient_id)
        rel_path = os.path.join(*parts[1:])
        # Use --all to avoid relying on a valid HEAD symbolic ref which
        # can be inconsistent in some environments (refs/heads/main vs master).
        try:
            commits = list(repo.iter_commits(rev='--all', paths=rel_path))
        except Exception:
            commits = list(repo.iter_commits(paths=rel_path))
        # chronological (oldest first)
        commits.reverse()
        result = []
        for c in commits:
            result.append({
                'hexsha': c.hexsha,
                'author': str(c.author),
                'message': c.message.strip(),
                'datetime': c.committed_datetime.isoformat(),
            })
        return result

    def head(self, relative_path: str) -> Optional[str]:
        parts = relative_path.split(os.sep)
        if len(parts) < 2:
            raise ValueError("relative_path must start with '<patient_id>/...'")
        patient_id = parts[0]
        repo = self._ensure_repo(patient_id)
        try:
            return repo.head.commit.hexsha
        except Exception:
            return None
