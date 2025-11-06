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
BHV (Behavioral Health Vault) is a lightweight Python web application for storing, viewing, and analyzing patient-provided images and associated narratives to help record recovery journeys for people with serious mental illnesses and related social determinants. It complements traditional EHRs by enabling uploads of photographs and scanned drawings along with textual narratives provided by patients or recorded by social workers.

Key goals:
- Minimal and easy to install
- Simple email-based signup and login (OTP support)
- Admin-level moderation and management
- Automatic sentiment analysis of narratives

Features
- Local signup (email/password) with OTP verification (console fallback when email is not configured)
- Optional Google OAuth sign-in
- Role-based access (admin / user)
- Upload images (required) and optional audio files; title and description for each upload
- Sentiment analysis using TextBlob with labels: positive, neutral, negative
- Files stored using MongoDB GridFS
- Admin dashboard with statistics and visualizations
- AJAX-based chat (polling) for comments/messages

Tech stack
- Backend: Flask
- Templates: Jinja2
- Database: MongoDB (PyMongo + GridFS)
- Auth: Flask-Login, Flask-WTF, bcrypt
- Email: Flask-Mail (OTP), console fallback supported
- Sentiment: TextBlob

Project layout (top-level)
```
app/                # application package (blueprints, models, utils, templates, static)
run.py              # application entry point
requirements.txt    # dependencies
seed_data.py        # optional seeding script
tests/              # pytest tests
README.md           # this file
```

### Authentication & Authorization
- Local signup with email/password + OTP verification
- Google OAuth login as an alternative
- Role-based access control (RBAC) with admin/user roles
- Secure password hashing with bcrypt

### Dashboard / Uploads
- Upload images (required) and optional audio files
- Title and description for each upload
- Automatic sentiment analysis using TextBlob
- Files stored in MongoDB GridFS
- Gallery view with thumbnails
- Detail view for each uploaded item

### Admin Dashboard
- Statistics on uploads by sentiment (positive, neutral, negative)
- Total uploads and users count
- View all uploads
- Chart.js visualization of sentiment distribution

### Chat
- AJAX-based chat between users and admin
- REST endpoints for sending and listing messages
- Real-time message updates (polling-based)

### Sentiment Analysis
- TextBlob-based sentiment analysis
- Automatic sentiment detection on upload
- Sentiment labels: positive, neutral, negative

## Tech Stack

- **Backend**: Flask, Jinja2 templates
- **Database**: MongoDB with PyMongo and GridFS
- **Authentication**: Flask-Login, Flask-WTF, Flask-Mail
- **OAuth**: Authlib for Google OAuth
- **Sentiment Analysis**: TextBlob
- **Frontend**: Minimal CSS/JS, Chart.js for statistics

## Project Structure

```
bhv/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── extensions.py        # Flask extensions
│   ├── models.py            # Database models
│   ├── utils.py             # Utility functions
│   ├── sentiment/           # Sentiment analysis module
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── textblob_provider.py
│   ├── auth/                # Authentication module
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── uploads/             # Uploads module
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── admin/               # Admin module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── chat/                # Chat module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/           # Jinja2 templates
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── uploads/
│   │   └── admin/
│   └── static/              # Static files
│       ├── css/
│       └── js/
├── tests/                   # Test files
├── seed_data.py             # Database seeding script
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables example
└── README.md               # This file
```

## Installation

1. **Clone the repository** (or ensure you have the project files)

2. **Install MongoDB**
   - Make sure MongoDB is running on your system
   - Default connection: `mongodb://localhost:27017`

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration:
   - MongoDB URI
   - Email server settings (for OTP)
   - Google OAuth credentials (optional)
   - Secret key

6. **Download TextBlob data**
   ```bash
   python -m textblob.download_corpora
   ```

7. **Seed database (optional)**
   ```bash
   python seed_data.py
   ```

8. **Run the application**
   ```bash
   python run.py
   ```

9. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

- `SECRET_KEY`: Flask secret key for session management
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB`: Database name
- `ADMIN_EMAILS`: Comma-separated list of admin email addresses (e.g., `admin1@example.com,admin2@example.com`)
  - **Important**: Only emails in this list will have admin access
  - **Dynamic Check**: Admin status is checked at runtime from this list
  - If you add a user's email to `ADMIN_EMAILS`, they immediately get admin access (no database changes needed)
  - Admin accounts cannot be created through registration form
  - Admin users must log in via Google OAuth or be created manually using `create_admin.py`
- `MAIL_SERVER`: SMTP server for email
- `MAIL_PORT`: SMTP port (usually 587)
- `MAIL_USERNAME`: Email address for sending OTPs
- `MAIL_PASSWORD`: Email password or app password
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (optional)
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret (optional)
- `OTP_EXPIRY_MINUTES`: OTP expiration time (default: 10)

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:5000/auth/google-callback`
6. Copy Client ID and Client Secret to `.env`

### Email Setup (for OTP)

The application requires email configuration to send OTP codes. However, if email is not configured, OTP codes will be printed to the console/terminal for development purposes.

**For Production - Gmail Setup:**
1. Go to your Google Account settings
2. Enable 2-factor authentication
3. Generate an app-specific password:
   - Go to Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Copy the 16-character password
4. Add to `.env` file:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

**For Development (No Email Setup):**
- If `MAIL_USERNAME` and `MAIL_PASSWORD` are not set in `.env`, OTP codes will be automatically displayed in the console/terminal where you run the Flask app
- Look for output like:
  ```
  ============================================================
  OTP for user@example.com: 123456
  OTP will expire in 10 minutes
  ============================================================
  ```

**Other Email Providers:**
- **Outlook/Hotmail**: Use `smtp-mail.outlook.com` with port `587`
- **Yahoo**: Use `smtp.mail.yahoo.com` with port `587`
- **Custom SMTP**: Update `MAIL_SERVER` and `MAIL_PORT` accordingly

## Usage

### User Registration

1. Navigate to `/auth/register`
2. Fill in email and password (only regular user accounts can be created)
3. Check email for OTP code (or check console if email not configured)
4. Enter OTP at `/auth/verify-otp`
5. Account will be verified and you'll be logged in

**Note**: Admin accounts cannot be created through registration. They must be:
- Configured via `ADMIN_EMAILS` in `.env` file
- Created using `python create_admin.py <email> <password>` script
- Created via Google OAuth (if email is in ADMIN_EMAILS list)

### Google OAuth Login

1. Click "Login with Google" on login page
2. Authorize the application
3. Account will be created automatically if it doesn't exist

### Uploading Content

1. Navigate to `/uploads/upload` (requires login)
2. Fill in title and description
3. Upload an image (required)
4. Optionally upload an audio file
5. Sentiment will be analyzed automatically
6. View in gallery at `/uploads/gallery`

### Admin Dashboard
 
1. Login as admin user
2. Navigate to `/admin/dashboard`
3. View statistics and recent uploads

### Chat

1. Open any upload detail page
2. Scroll to chat section
3. Send messages (AJAX-based)
4. Messages refresh automatically every 3 seconds

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Development

The application uses Flask's development server. For production, consider using:
- Gunicorn or uWSGI for WSGI server
- Nginx as reverse proxy
- SSL/TLS certificates
- Proper secret key management
- Database backups

## License

This project is provided as-is for educational and development purposes.

## Notes

- The application is lightweight and does not use heavy ML libraries
- WebSocket is not used; chat uses AJAX polling
- Sentiment analysis uses TextBlob only
- All file uploads are stored in MongoDB GridFS
- UI theme: White and Yellow
