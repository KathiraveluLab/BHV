class Conflict(Exception):
    """Raised when an optimistic-lock parent does not match the repository HEAD."""
    pass
