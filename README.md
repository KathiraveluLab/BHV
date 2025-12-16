# BHV: Behavioral Health Vault

The goal of this project is to provide a digitization approach to record the journey of recovery of people with serious mental illnesses and other social determinants. BHV (pronounced Beehive or Behave) aims to complement traditional Electronic Health Records (EHRs) by storing patient-provided images (photographs and scanned drawings) along with associated textual narratives, which may be provided by the patient or recorded by a social worker during an interview.

BHV is a minimal, Python-based application that enables healthcare networks to store and retrieve patient-provided images.

It provides them access to upload, view, and edit their own images and narratives.

It also provides admin-level access for system administrators to view the entire ecosystem, upload images on behalf of users, along with the narrative, edit images on behalf of users, and delete images or narrations on behalf of users or as a moderation action.

The system should be secure. But the signup process should be pretty straightforward. Email-based signups are ok. 

Log-ins should be straightforward. A simple username and password should be sufficient.

The system should avoid unnecessary bloat to enable easy installation in healthcare networks.

The front-end should be kept minimal to allow the entire system to be run from a single command (rather than expecting the front-end, backend, and database to be run separately).

The storage of the images could be in a file system with an index to retrieve them easily. The index itself could be in a database to allow easy queries.

## Changes Implemented

- Frontend migrated to React using Vite in `frontend/` with a modern layout, Inter font, and simple card gallery.
- Backend updated to serve built React assets from `frontend/dist` and provide JSON APIs.
- New JSON endpoints: `GET /api/images`, `POST /api/login`, `POST /api/logout`, `POST /api/upload`, `POST /api/signup`.
- Minimal FastAPI app scaffolded: `app.py`, models in `bhv/models.py`, storage in `bhv/storage.py`, auth in `bhv/auth.py`, and DB helpers in `bhv/db.py`.
- Static fallback retained; images served from `data/images` with thumbnails.
- Project dependencies added in `requirements.txt`; `.gitignore` updated for frontend build and node modules.

## Security Configuration

**IMPORTANT:** Before running the application, you must set the `BHV_SECRET` environment variable with a strong, random secret key. This is used to secure session data and prevent tampering.

1. Generate a secure secret key:
   ```
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set the environment variable with the generated key:
   - **Windows (PowerShell):** `$env:BHV_SECRET = "your-generated-key"`
   - **Windows (CMD):** `set BHV_SECRET=your-generated-key`
   - **Linux/Mac:** `export BHV_SECRET="your-generated-key"`

3. Alternatively, create a `.env` file by copying `.env.example` and filling in your secret key.

The application will fail to start if `BHV_SECRET` is not set, preventing accidental use of insecure defaults.

## Run Instructions

- Backend:
	- `python -m venv .venv`
	- `\.venv\Scripts\Activate`
	- `pip install -r requirements.txt`
	- Set `BHV_SECRET` environment variable (see Security Configuration above)
	- `python app.py`

- Frontend (development):
	- `cd frontend`
	- `npm install`
	- `npm run dev`

- Frontend (production build served by backend):
	- `cd frontend`
	- `npm install`
	- `npm run build`
	- `cd ..`
	- `python app.py`

## Notes

- React UI focuses on simplicity and minimal bloat while keeping a clean look suitable for healthcare environments.
- For separate dev servers, add CORS to FastAPI or use Vite proxy as needed.
