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

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Python App     │◄──►│   File System   │
│  (Minimal UI)   │    │  (Flask)         │    │  (Image Store)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │ (Metadata Index)│
                       └─────────────────┘
```

**Components:**
- **Web Interface**: Minimal HTML templates for user/admin interactions
- **Python Application**: Core logic handling authentication, file operations, and database queries
- **File System Storage**: Direct file storage for images with organized directory structure
- **SQLite Database**: Lightweight indexing for metadata, user management, and quick queries

## Project Structure

```
BHV/
├── app.py              # Main application entry point
├── config/             # Configuration management
├── models/             # Database models (users, images, narratives)
├── views/              # Web interface handlers
├── templates/          # Minimal HTML templates
├── static/             # CSS, JS (minimal)
├── utils/              # Helper functions
├── data/               # SQLite database files
├── media/              # User-uploaded content
│   └── uploads/        # Organized by user/date
├── logs/               # Application logs
├── docs/               # Documentation
└── tests/              # Test suite
```

## Project Status

**Current Phase: Foundation & Documentation**

**MVP Features (Planned):**
- User authentication (email-based signup, username/password login)
- Image upload with narrative text
- Personal gallery (view/edit own content)
- Admin dashboard (view/moderate all content)
- Secure file access control

**Future Enhancements:**
- Advanced search and filtering
- Bulk operations for administrators
- Integration APIs for EHR systems
- Enhanced security features (2FA, audit logging)
- Mobile-responsive interface improvements

## Single-Command Philosophy

BHV is designed for **simple deployment** in healthcare networks:

```bash
python app.py  # Starts everything: web server, database, file handling
```

**Why Single-Command?**
- **Reduced complexity**: No separate frontend/backend/database setup
- **Healthcare-friendly**: IT departments prefer unified deployment
- **Minimal dependencies**: Self-contained Python application
- **Quick testing**: Developers can run entire system instantly

The application automatically:
- Initializes the database if needed
- Creates required directories
- Starts the web server
- Handles all routing and file operations

## Getting Started

See [Setup & Environment Guide](docs/setup.md) for installation and configuration instructions.
