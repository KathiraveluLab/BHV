# 🏥 Data & Storage Model

> **Healthcare-Grade Data Architecture for Patient Recovery Journey Documentation**

## 🎯 Executive Summary

BHV implements a **hybrid storage architecture** combining relational database indexing with filesystem-based image storage, specifically engineered for healthcare network requirements and **HIPAA compliance**. This design ensures optimal performance, regulatory adherence, and scalable patient data management.

## 🏗️ Storage Architecture

### 🔄 Hybrid Storage Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                 🎯 APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  📊 SQLite Database     │      📁 File System              │
│  (Metadata Index)       │     (Image Storage)               │
│                         │                                   │
│  👥 User records        │  🖼️ Original images              │
│  📋 Image metadata      │  🔍 Generated thumbnails          │
│  📝 Narratives          │  📊 Raw EXIF data (JSON)         │
│  🔍 Audit trails        │  ⏳ Temporary uploads             │
└─────────────────────────────────────────────────────────────┘
```

### 🔗 Data Relationships
```
👤 users (1) ──────── (N) 🖼️ images (1) ──────── (N) 📝 narratives
  │                           │
  │                           └── 📋 audit_logs (comprehensive trail)
  │
  └── 🔐 audit_logs (user management)
```

## 📊 Database Storage Model

### 📋 Table Specifications

#### 👥 Users Table - **Patient & Staff Management**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,        -- bcrypt hashed
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,             -- Account status
    email_verified BOOLEAN DEFAULT FALSE,       -- Email verification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,                       -- Activity tracking
    profile_data TEXT                           -- JSON: preferences, settings
);
```

#### 🖼️ Images Table - **Patient Recovery Documentation**
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,        -- Patient's original filename
    file_path VARCHAR(500) NOT NULL,            -- Secure storage path
    thumbnail_path VARCHAR(500),                -- Gallery optimization
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(50) NOT NULL,
    width INTEGER,                              -- Image dimensions
    height INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,             -- Soft delete support
    privacy_level TEXT CHECK(privacy_level IN ('private', 'shared_with_staff')) DEFAULT 'private'
);
```

#### 📝 Narratives Table - **Recovery Journey Stories**
```sql
CREATE TABLE narratives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    content TEXT NOT NULL,                      -- Patient's story/description
    author_type TEXT CHECK(author_type IN ('patient', 'social_worker', 'admin')) DEFAULT 'patient',
    author_id INTEGER REFERENCES users(id),     -- Who wrote this narrative
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Updated via application logic/trigger
);

-- SQLite trigger for automatic updated_at timestamp
CREATE TRIGGER update_narratives_timestamp 
    AFTER UPDATE ON narratives
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE narratives SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

#### 📋 Audit Logs Table - **HIPAA Compliance Audit Trail**
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),      -- Any user (patient, social worker, admin)
    action VARCHAR(100) NOT NULL,              -- 'create', 'update', 'delete', 'view', 'login'
    resource_type VARCHAR(50),                 -- 'user', 'image', 'narrative', 'session'
    resource_id INTEGER,                       -- ID of affected record
    old_values TEXT,                           -- JSON: previous state for compliance
    new_values TEXT,                           -- JSON: new state for compliance
    description TEXT,                          -- Human-readable action description
    ip_address VARCHAR(45),                    -- Security tracking
    user_agent TEXT,                           -- Browser/device info
    session_id VARCHAR(255),                   -- Session correlation
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## File System Storage Model

### Directory Structure
```
media/
├── uploads/
│   └── users/
│       └── {user_id}/
│           └── {year}/
│               └── {month}/
│                   ├── images/
│                   │   ├── {image_id}_original.{ext}
│                   │   └── {image_id}_thumb.jpg
│                   └── metadata/
│                       └── {image_id}_exif.json
├── temp/
│   └── uploads/        # Temporary processing area
└── backups/
    └── {date}/         # Automated backup storage
```

### File Naming Convention
- **Original Images**: `{image_id}_original.{extension}`
- **Thumbnails**: `{image_id}_thumb.jpg`
- **EXIF Metadata**: `{image_id}_exif.json`

### Storage Features

#### Image Processing Pipeline
1. **Upload Validation**: File type, size, and format verification
2. **Virus Scanning**: Optional integration with antivirus systems
3. **EXIF Extraction**: Metadata extraction and sanitization
4. **Thumbnail Generation**: Standardized preview images (200x200px)
5. **Secure Storage**: Organized placement in user-specific directories
6. **Database Indexing**: Metadata insertion for quick queries

#### File Access Control
- **User Isolation**: Each user has dedicated directory structure
- **Permission Model**: Application-controlled access only
- **Direct Access Prevention**: No direct web server file serving
- **Audit Trail**: All file operations logged in audit_logs table

## Data Lifecycle Management

### Upload Process
```
1. User uploads image → 2. Validation & scanning → 3. EXIF extraction
                                    ↓
6. Database indexing ← 5. Secure file storage ← 4. Thumbnail generation
```

### Data Retention Policy
- **Active Images**: Retained indefinitely while user account is active
- **Deleted Images**: Soft delete with 30-day recovery period
- **User Account Deletion**: Complete data purge after 90-day retention
- **Audit Logs**: Retained for 7 years for compliance requirements

### Backup Strategy
- **Database Backups**: Daily automated SQLite database dumps
- **File System Backups**: Weekly incremental image storage backups
- **Offsite Storage**: Encrypted backup replication for disaster recovery
- **Recovery Testing**: Monthly backup restoration validation

## Performance Considerations

### Database Optimization
```sql
-- Performance indexes
CREATE INDEX idx_images_user_id ON images(user_id);
CREATE INDEX idx_images_upload_date ON images(upload_date);
CREATE INDEX idx_narratives_image_id ON narratives(image_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_users_email ON users(email);
```

### File System Optimization
- **Directory Sharding**: Date-based organization prevents large directory issues
- **Thumbnail Caching**: Pre-generated thumbnails for fast gallery loading
- **Lazy Loading**: On-demand full-size image loading
- **CDN Ready**: Structure supports future CDN integration

## Scalability Architecture

### Horizontal Scaling Options
- **Database Sharding**: User-based database partitioning
- **File Storage Distribution**: Multi-server file storage with load balancing
- **Read Replicas**: Database read scaling for high-traffic scenarios
- **Caching Layer**: Redis integration for session and metadata caching

### Healthcare Network Considerations
- **HIPAA Compliance**: Audit trails and access controls built-in
- **Network Isolation**: Support for air-gapped healthcare networks
- **Minimal Dependencies**: Self-contained deployment requirements
- **Compliance Reporting**: Built-in audit trail export capabilities

## Why This Architecture?

### Database + Filesystem Hybrid Benefits
- **Query Performance**: Fast metadata searches via database indexes
- **Storage Efficiency**: Direct file storage without database bloat
- **Backup Simplicity**: Separate backup strategies for data types
- **Compliance**: Clear audit trails and data lineage

### Healthcare-Specific Advantages
- **Regulatory Compliance**: Built-in audit trails and data retention
- **Network Compatibility**: Works in restricted healthcare environments
- **Minimal Complexity**: Reduces IT department deployment burden
- **Data Portability**: Standard formats enable easy migration