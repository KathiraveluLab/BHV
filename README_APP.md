# BHV — Alaska (Minimalist Immutable Patient Records Platform)

A minimal Flask-based prototype for immutable, versioned storage of patient health records using Git as the backend storage system.

## Features

- **Git-backed storage**: Every file save creates an immutable Git commit with metadata (user, timestamp, action).
- **Version history & diffs**: View complete edit history and unified diffs between any two versions.
- **User authentication**: 
  - Email/password signup and login with password strength validation
  - Google OAuth Sign-In for quick account creation/login
  - Role-based access (patients view own entries, admins see all)
- **File management**: Upload files with narrative notes; organize by patient ID.
- **Database abstraction**: Uses MongoDB if configured, falls back to embedded TinyDB for zero-setup deployments.
- **Alaska theme**: Minimal, clean UI with teal accents; responsive design.

## Quick Start

### Prerequisites

- Python 3.8+
- Git

### Setup (5 minutes)

1. **Clone and enter the repo**:
   ```bash
   cd BHV
   ```

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Configure environment**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to set `GOOGLE_CLIENT_ID` (for OAuth) or `MONGO_URI` (for MongoDB). Both are optional.
   - If `.env` is missing, the app uses defaults: `TinyDB` (embedded) and no Google OAuth.

5. **Run the app**:
   ```powershell
   D:/.venv/Scripts/python.exe run.py
   ```
   Or directly:
   ```powershell
   $env:FLASK_APP='bhv.full_app:create_app'
   D:/.venv/Scripts/python.exe -m flask run --reload --host=127.0.0.1 --port=5000
   ```

6. **Open in browser**:
   - Visit http://127.0.0.1:5000
   - Click **Get started** and create an account (email/password or Google OAuth)
   - Upload a file + narrative note
   - View history, diffs, and download previous versions

### Demo Flow

1. **Signup**: Create a patient or admin account
2. **Upload**: Add a file with narrative notes (creates Git commit #1)
3. **Edit**: Upload the same file again with updated content (creates Git commit #2)
4. **History**: Click file → view commit timeline with authors, timestamps, messages
5. **Diff**: Compare two versions side-by-side (unified diff format)
6. **Download**: Download any specific version from the history view

## Project Structure

```
BHV/
├── run.py                        # App entrypoint
├── requirements.txt              # Python dependencies
├── .env.example                  # Configuration template
├── bhv/
│   ├── __init__.py
│   ├── full_app.py              # Flask app factory with all routes
│   ├── db.py                    # DB abstraction (MongoDB/TinyDB)
│   ├── app.py                   # Demo mini-app (legacy)
│   └── storage/
│       ├── base.py              # StorageAdapter interface
│       ├── git_adapter.py        # Git-backed implementation
│       └── errors.py            # Custom exceptions
├── templates/                    # Jinja2 templates
│   ├── base.html                # Base layout with header/nav/footer
│   ├── index.html               # Landing page
│   ├── signup.html              # Signup form + Google Sign-In
│   ├── login.html               # Login form + Google Sign-In
│   ├── upload.html              # File upload form
│   ├── patient.html             # Patient's entries view
│   ├── admin.html               # Admin: all entries view
│   ├── history.html             # Version history with diffs
│   └── diff.html                # Unified diff viewer
├── static/
│   └── css/
│       └── alaska.css           # Alaska theme stylesheet
├── data/
│   ├── db.json                  # TinyDB file (auto-created)
│   └── storage/                 # Per-patient Git repos
├── uploads/                     # Uploaded files + Git repos
└── tests/                       # Unit & integration tests
```

## Configuration

### Environment Variables (in `.env`)

```
SECRET_KEY=your-secret-key-here          # Session encryption key
FLASK_ENV=development                    # 'development' or 'production'
MONGO_URI=mongodb://...                  # Optional MongoDB connection
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com  # Optional Google OAuth
```

**Defaults** (if `.env` is missing):
- `SECRET_KEY`: `'dev-secret-change-in-prod'`
- `FLASK_ENV`: `'development'` (no HTTPS required for cookies)
- **DB**: Embedded TinyDB at `data/db.json`
- **OAuth**: Disabled (email/password auth only)

### Google OAuth Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create an OAuth 2.0 Web Application
3. Add authorized redirect URI: `http://localhost:5000/` (for local dev)
4. Copy the **Client ID** into `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```
5. Reload the app; Google Sign-In buttons will now appear on login/signup pages

## API Routes

### Authentication
- `POST /signup` — Create a new account
- `POST /login` — Sign in with email/password
- `GET /logout` — Clear session
- `POST /auth/google` — Google OAuth token verification (auto-creates account)

### Upload & Entries
- `GET /upload` — Upload form
- `POST /upload` — Save file to Git + DB
- `GET /my` — Patient's entries list
- `GET /admin` — Admin: all entries (admins only)

### Versioning & Download
- `GET /history/<patient_id>/<filename>` — View commit history
- `GET /diff/<patient_id>/<filename>/<old_sha>/<new_sha>` — Unified diff
- `GET /file/<patient_id>/<filename>` — Download latest version
- `GET /file/<patient_id>/<filename>/<commit_sha>` — Download specific commit

## Security Notes

- **CSRF tokens**: All forms are protected with flask-wtf
- **Password hashing**: Uses Werkzeug's `generate_password_hash` (PBKDF2 by default)
- **Session cookies**: HttpOnly, SameSite=Lax, Secure in production
- **Email validation**: Basic RFC 5322 regex validation
- **Password strength**: Minimum 6 characters (enforced server-side)
- **Google OAuth**: Tokens verified server-side using `google-auth-oauthlib`

**Production hardening checklist**:
- [ ] Set `SECRET_KEY` to a random, long string
- [ ] Set `FLASK_ENV=production` and use HTTPS
- [ ] Use MongoDB instead of TinyDB for persistence
- [ ] Deploy behind a reverse proxy (nginx, Gunicorn)
- [ ] Add rate limiting on login/signup endpoints
- [ ] Enable database backups and Git repo backups
- [ ] Run tests before deployment

## Testing

Run unit and integration tests:

```bash
D:/.venv/Scripts/python.exe -m pytest tests/ -v
```

Run the demo:

```bash
D:/.venv/Scripts/python.exe scripts/demo_run.py
```

## Troubleshooting

### "TemplateNotFound: index.html"
- Ensure the Flask server is restarted after adding/modifying templates
- Check that `templates/` directory exists at project root

### "ModuleNotFoundError: No module named 'tinydb'"
- Install dependencies: `pip install -r requirements.txt`

### Google OAuth not appearing
- Ensure `GOOGLE_CLIENT_ID` is set in `.env`
- Clear browser cache and reload

### Files not appearing after upload
- Check `uploads/` directory exists and is writable
- Check `data/db.json` for database entries
- Review Flask logs for errors

## Development

### File a new feature
1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make changes, test locally
3. Commit with a clear message
4. Push to your fork and open a PR against `dev`

### Run with auto-reload (development):
```powershell
$env:FLASK_ENV='development'
D:/.venv/Scripts/python.exe -m flask run --reload
```

## License

See `LICENSE` file.

## Contributing

See `CONTRIBUTING.md` for guidelines.

---

**Built with** Flask, GitPython, TinyDB/MongoDB, and Jinja2 templates.
