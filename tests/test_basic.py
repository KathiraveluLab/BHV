"""Basic tests to verify setup."""
import pytest


def test_imports():
    """Test that bhv package can be imported."""
    try:
        import bhv
        assert True
    except ImportError:
        assert False, "bhv package should be importable"


def test_python_version():
    """Verify Python version is 3.7+."""
    import sys
    assert sys.version_info >= (3, 7), "Python 3.7+ required"