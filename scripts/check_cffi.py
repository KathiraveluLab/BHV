import sys

print("PYTHON:", sys.executable)

try:
    import cffi
    print("cffi:", getattr(cffi, "__file__", "no file"), getattr(cffi, "__version__", "n/a"))
except Exception as e:
    print("cffi import error:", repr(e))

try:
    import cryptography
    print("cryptography OK")
except Exception as e:
    print("cryptography import error:", repr(e))

try:
    import _cffi_backend
    print("_cffi_backend available")
except Exception as e:
    print("_cffi_backend import error:", repr(e))
