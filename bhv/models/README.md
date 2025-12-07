# BHV Database Models

This directory contains the SQLAlchemy models for BHV.

## Models

### User (`user.py`)
- Stores user authentication and profile information
- Roles: patient, social_worker, admin
- Relationships: images, audit_logs

### Image (`image.py`)
- Stores image metadata and file paths
- Supports local and GitHub storage
- Includes file hash for duplicate detection
- Relationships: user, narratives

### Narrative (`narrative.py`)
- Stores patient narratives associated with images
- Tracks who created the narrative
- Maintains edit history

### AuditLog (`audit_log.py`)
- HIPAA compliance audit trail
- Logs all admin actions
- Stores IP address and timestamp

## Database Schema
```
users
├── id (PK)
├── email (UNIQUE)
├── password_hash
├── role
└── created_at

images
├── id (PK)
├── user_id (FK → users.id)
├── file_path
├── storage_type
├── file_hash
└── upload_date

narratives
├── id (PK)
├── image_id (FK → images.id)
├── content
├── created_by (FK → users.id)
└── last_modified

audit_logs
├── id (PK)
├── admin_id (FK → users.id)
├── action
├── target_user_id (FK → users.id)
├── target_image_id (FK → images.id)
└── timestamp
```

## Initialization

Run the initialization script to create all tables:
```bash
python scripts/init_db.py
```
```

5. Save

---

### **Step 5: Check Your File Structure**

Your structure should now look like this:
```
BHV/
├── bhv/
│   ├── __init__.py
│   ├── database.py          ← NEW
│   ├── models/
│   │   ├── __init__.py      ← UPDATED
│   │   ├── user.py          ← NEW
│   │   ├── image.py         ← NEW
│   │   ├── narrative.py     ← NEW
│   │   ├── audit_log.py     ← NEW
│   │   └── README.md        ← NEW
│   ├── views/
│   │   └── __init__.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── utils/
│       └── __init__.py
├── scripts/
│   ├── __init__.py          ← NEW
│   └── init_db.py           ← NEW
├── tests/
│   ├── __init__.py
│   └── test_basic.py
├── docs/
│   └── installation.md
├── .gitignore
├── requirements.txt         ← UPDATED
├── CONTRIBUTING.md
└── README.md