# BHV Setup Guide

This file contains setup and run instructions for the BHV.

## Stack

- Backend: Python, FastAPI
- Frontend: Jinja2 templates + HTML/CSS
- Database: MongoDB with PyMongo
- Auth: JWT + password hashing (passlib bcrypt)
- Storage: local filesystem in `storage/images/{user_id}/`

## Project Structure

```text
bhv/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── upload.py
│   │   ├── gallery.py
│   │   └── admin.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── image_service.py
│   ├── templates/
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   └── gallery.html
│   └── static/css/style.css
├── storage/images/
├── requirements.txt
├── run.py
└── SETUP.md
```

## Setup

1. Install MongoDB and make sure it is running.
2. Create and activate a Python virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` as needed.

Variables:

```bash
MONGO_URI="mongodb://localhost:27017"
DATABASE_NAME="bhv_db"
JWT_SECRET_KEY="replace-with-a-strong-secret"
ACCESS_TOKEN_EXPIRE_MINUTES="60"
```

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`