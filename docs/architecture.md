# System Architecture & Design Overview

## Overview

BHV follows a layered architecture designed for healthcare network deployment with emphasis on simplicity, security, and maintainability. The system separates concerns across presentation, business logic, data persistence, and file storage layers.

## Backend Architecture

### Python Application Layer
- **Framework**: Flask web framework for lightweight HTTP handling
- **Authentication**: Session-based user management with secure password hashing
- **File Processing**: Image upload validation, storage, and retrieval operations
- **Database Operations**: SQLite ORM for metadata management and user data
- **Configuration Management**: Environment-based configuration for deployment flexibility

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│  Authentication │  File Handler  │  Database ORM  │ Config │
├─────────────────────────────────────────────────────────────┤
│              Business Logic Layer                           │
├─────────────────────────────────────────────────────────────┤
│   User Service  │ Image Service │ Narrative Service │ Admin │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Minimal Template System
- **Technology**: Jinja2 templates with minimal JavaScript
- **Design Philosophy**: Server-side rendering for reduced complexity
- **Responsive Design**: Basic CSS for cross-device compatibility
- **User Interface**: Clean, healthcare-appropriate interface design

### Template Structure
```
templates/
├── base.html           # Common layout and navigation
├── auth/
│   ├── login.html      # User authentication
│   └── register.html   # User registration
├── user/
│   ├── gallery.html    # Personal image gallery
│   ├── upload.html     # Image upload interface
│   └── edit.html       # Content editing
└── admin/
    ├── dashboard.html  # Administrative overview
    ├── users.html      # User management
    └── moderation.html # Content moderation
```

## Image Storage System

### File System Organization
```
media/uploads/
├── users/
│   └── {user_id}/
│       └── {year}/
│           └── {month}/
│               ├── {image_id}.jpg
│               ├── {image_id}_thumb.jpg
│               └── metadata.json
└── temp/               # Temporary upload processing
```

### Storage Features
- **Organized Structure**: User-based directory hierarchy with date organization
- **Thumbnail Generation**: Automatic thumbnail creation for gallery views
- **Raw EXIF Preservation**: Complete EXIF data stored in metadata.json for archival purposes
- **File Validation**: Image format verification and size limits
- **Access Control**: Directory-level permissions for security

### Metadata Storage Strategy
- **Database**: Stores indexed, queryable metadata (file paths, sizes, upload dates, user associations)
- **metadata.json**: Preserves complete raw EXIF data and technical image properties for archival and potential future analysis
- **Single Source of Truth**: Database serves as authoritative source for application queries; JSON files provide comprehensive technical backup

## Metadata Indexing (Database)

### Database Schema
```sql
-- User Management
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Image Records
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(50),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Narrative Content
CREATE TABLE narratives (
    id INTEGER PRIMARY KEY,
    image_id INTEGER REFERENCES images(id),
    content TEXT,
    author_type TEXT CHECK(author_type IN ('patient', 'social_worker')) DEFAULT 'patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin Actions (Audit Trail)
CREATE TABLE admin_actions (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## User Roles & Permissions

### Patient/User Role
**Capabilities:**
- Register account with email verification
- Upload images with narrative descriptions
- View personal gallery of uploaded content
- Edit own narrative content
- Delete own images and narratives
- Update profile information

**Restrictions:**
- Cannot access other users' content
- Cannot perform administrative functions
- Limited to personal content management

### Administrator Role
**Capabilities:**
- View all user accounts and content
- Upload images on behalf of any user
- Edit narratives for any user
- Delete any content (moderation actions)
- Manage user accounts (activate/deactivate)
- Access system logs and audit trails
- Configure system settings

**Responsibilities:**
- Content moderation and compliance
- User support and account management
- System maintenance and monitoring
- Data privacy and security oversight

## Security Architecture

### Authentication & Authorization
- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure session cookies with expiration
- **Role-Based Access**: Decorator-based permission checking
- **CSRF Protection**: Token-based form validation

### File Security
- **Upload Validation**: File type and size restrictions
- **Path Traversal Prevention**: Sanitized file naming
- **Direct Access Prevention**: Protected file serving through application
- **Virus Scanning**: Optional integration for uploaded files

### Data Protection
- **Database Encryption**: Planned enhancement using SQLCipher for sensitive data protection
- **Audit Logging**: Comprehensive action tracking
- **Privacy Controls**: User consent and data retention policies
- **Backup Security**: Encrypted backup procedures

## Deployment Architecture

### Single-Command Deployment
```bash
python app.py
```

**Initialization Process:**
1. Load environment configuration
2. Initialize database schema if needed
3. Create required directory structure
4. Start Flask development/production server
5. Enable file serving and routing

### Healthcare Network Considerations
- **Minimal Dependencies**: Self-contained Python application
- **Network Security**: HTTPS enforcement in production
- **Compliance Ready**: HIPAA-consideration in design
- **Scalability**: Horizontal scaling through load balancing
- **Monitoring**: Built-in logging and health checks