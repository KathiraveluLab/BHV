from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, relative_path: str, data: bytes, user_id: str, action: str, message: Optional[str] = None) -> str:
        """Save bytes into storage and return a version id / commit hash."""

    def save_with_parent(self, relative_path: str, data: bytes, user_id: str, action: str, parent: Optional[str] = None, message: Optional[str] = None) -> str:
        """Save bytes with optimistic locking using a parent commit hash. If parent is provided, the adapter should verify
        that the repository HEAD matches parent before committing. Returns new commit hash."""

    @abstractmethod
    def get(self, relative_path: str, version: Optional[str] = None) -> bytes:
        """Retrieve file bytes. If version is None, return latest."""

    @abstractmethod
    def history(self, relative_path: str) -> List[Dict]:
        """Return chronological list of versions/commits for the given path."""

    def head(self, relative_path: str) -> Optional[str]:
        """Return the current HEAD commit hexsha for the path's repository, or None if none exists."""
