# Behavioral Health Vault (BHV) Prototype

A secure, calming web application for documenting your behavioral health journey. Built with React, Flask, and SQLite.

## Project Structure

- `frontend/`: React application (Vite, Tailwind CSS)
- `backend/`: Flask REST API (SQLAlchemy, SQLite, JWT)

## Prerequisites

- Python 3.8+
- Node.js 16+

## Setup & Run

### Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   python app.py
   ```
   The API will run at `http://localhost:5000`.

### Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will open at `http://localhost:5173`.

## Features

- **Authentication**: Secure signup and login with email/password (Bcrypt hashing, JWT).
- **Dashboard**: Personal overview of your vault.
- **Image Upload**: Upload images with narrative descriptions stored locally.
- **Gallery**: View your journey timeline.
- **Privacy**: Data is stored locally in SQLite and the filesystem.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Axios
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Bcrypt, PyJWT
- **Database**: SQLite
