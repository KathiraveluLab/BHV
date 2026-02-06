# Git-backed Storage Adapter (draft)

This directory contains a minimal demo implementation of a Git-backed storage adapter for BHV.

Key ideas:
- Each patient's vault is a separate local Git repository under `data/storage/<patient_id>/`.
- Every save creates a file write + `git add` + `git commit` with metadata in the commit message.
- The `GitAdapter` exposes `save`, `get`, and `history` methods.

How to try locally:

1. Create a virtual environment and install requirements:

```powershell
python -m venv .venv; 
.\.venv\Scripts\Activate.ps1; 
pip install -r requirements.txt
```

2. Run the demo Flask app:

```powershell
python -m bhv.app
```

3. Upload a file via curl / HTTP client:

```powershell
curl -F "patient_id=patient1" -F "user_id=sw123" -F "action=narrative-update" -F "file=@C:\path\to\image.jpg" http://localhost:5000/upload
```

4. View history:

```powershell
curl http://localhost:5000/history/patient1/image.jpg
```

Notes and next steps:
- This is a minimal demo used to prototype the approach. For production use:
  - Integrate with existing upload routes and MongoDB index.
  - Add proper authentication and authorization checks.
  - Add concurrency handling beyond a simple lock when scaling across processes.
  - Consider signing commits or pushing to a remote git server for true tamper-evidence.
