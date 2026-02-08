# 🔒 Security & Privacy Model

> **Enterprise-Grade Security Framework for Healthcare Patient Data Protection**

## 🎯 Executive Summary

BHV implements a **defense-in-depth security architecture** specifically designed for healthcare environments, ensuring **HIPAA compliance**, patient data protection, and secure system operations. This comprehensive framework addresses authentication, authorization, data protection, and regulatory compliance requirements.

## 🔐 Authentication Security

### 🚪 User Authentication Flow
```
📝 Registration → 📧 Email Verification → 🔑 Password Policy → ✅ Account Activation
     ↓              ↓                    ↓              ↓
🔒 Multi-factor ← 🔄 Session Management ← 🚪 Login Attempt ← 🔄 Account Recovery
```

### 🔑 Password Security - **Healthcare Grade**
- **💪 Hashing Algorithm**: bcrypt with configurable work factor (minimum 12)
- **📏 Password Requirements**: Minimum 12 characters, mixed case, numbers, symbols
- **📅 Password History**: Prevent reuse of last 5 passwords
- **🚫 Account Lockout**: 5 failed attempts trigger 15-minute lockout
- **⏰ Password Expiration**: Optional 90-day rotation for admin accounts

### 🔄 Session Management - **Secure by Design**
```python
# 🔒 Production Security Configuration
SESSION_COOKIE_SECURE = True      # 🔒 HTTPS only
SESSION_COOKIE_HTTPONLY = True    # 🚫 No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict' # 🔒 CSRF protection
SESSION_PERMANENT = False         # 🔄 Browser session only
PERMANENT_SESSION_LIFETIME = 3600 # ⏰ 1 hour for persistent sessions
```

### 🔐 Multi-Factor Authentication (Roadmap)
- **📱 TOTP Support**: Time-based one-time passwords via authenticator apps
- **📲 SMS Backup**: Optional SMS-based second factor
- **🔑 Recovery Codes**: Single-use backup codes for account recovery
- **👥 Admin Requirement**: Mandatory MFA for administrative accounts

## 🔐 Authorization & Access Control

### 🏅 Role-Based Access Control (RBAC) - **Healthcare Optimized**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   🧑‍⚕️ Patient       │    │  👩‍⚕️ Social Worker  │    │  👨‍💼 Administrator  │
│                 │    │                 │    │                 │
│ 🖼️ Own images    │    │ 👥 Assigned      │    │ 🌍 All content   │
│ 📝 Own narratives│    │   patients      │    │ 👥 User mgmt     │
│ ⚙️ Profile mgmt  │    │ 📝 Add narratives│    │ ⚙️ System config │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📋 Permission Matrix - **HIPAA Compliant Access Control**
| 🎯 Action | 🧑‍⚕️ Patient | 👩‍⚕️ Social Worker | 👨‍💼 Admin |
|--------|---------|---------------|-------|
| 🖼️ Upload own images | ✅ | ❌ | ✅ |
| 🖼️ Upload image for assigned patient | ❌ | ✅ | ✅ |
| 👁️ View own images | ✅ | ❌ | ✅ |
| 👁️ View assigned patient images | ❌ | ✅ | ✅ |
| ✏️ Edit own narratives | ✅ | ❌ | ✅ |
| 📝 Add narrative for assigned patient | ❌ | ✅ | ✅ |
| ✏️ Edit narrative for assigned patient | ❌ | ✅ | ✅ |
| 🗑️ Delete any content | ❌ | ❌ | ✅ |
| 👥 Manage users | ❌ | ❌ | ✅ |
| 📋 View audit logs | ❌ | ❌ | ✅ |

### 💻 Access Control Implementation - **Code-Level Security**
```python
# 🔒 Decorator-based permission checking
@require_permission('view_image')
@require_ownership_or_admin
def view_image(image_id):
    # 👁️ Image viewing logic with access validation
    pass

@admin_required
@audit_action('delete_user_content')
def delete_user_content(user_id):
    # 🗑️ Administrative content management with audit trail
    pass
```

## Data Protection & Privacy

### Data Classification
- **Highly Sensitive**: Patient images, medical narratives, personal identifiers
- **Sensitive**: User account information, session data, audit logs
- **Internal**: System configuration, application logs, metadata
- **Public**: Static assets, documentation, error pages

### Encryption Standards

#### Data at Rest
- **Database Encryption**: Planned SQLCipher implementation with AES-256
- **File System Encryption**: OS-level encryption recommended (BitLocker/LUKS)
- **Backup Encryption**: AES-256 encrypted backup archives
- **Key Management**: Hardware Security Module (HSM) integration planned

#### Data in Transit
- **HTTPS Enforcement**: TLS 1.3 minimum, perfect forward secrecy
- **Certificate Management**: Automated Let's Encrypt or enterprise CA
- **HSTS Headers**: HTTP Strict Transport Security enabled
- **Certificate Pinning**: Planned for mobile applications

### Privacy Controls

#### Data Minimization
- **Collection Limitation**: Only necessary data collected
- **Purpose Limitation**: Data used only for stated healthcare purposes
- **Retention Limits**: Automated data purging based on retention policies
- **Anonymization**: Personal identifiers removed from analytics data

#### User Privacy Rights
- **Data Access**: Users can download their complete data archive
- **Data Portability**: Standard formats for easy data transfer
- **Data Correction**: Users can update personal information
- **Data Deletion**: Complete account and data removal on request

## Application Security

### Input Validation & Sanitization
```python
# File upload validation
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']

# Content validation
def validate_narrative_content(content):
    # XSS prevention, length limits, content filtering
    return sanitize_html(content, allowed_tags=['p', 'br'])
```

### Cross-Site Request Forgery (CSRF) Protection
- **Token-Based Protection**: Unique tokens for all state-changing operations
- **SameSite Cookies**: Additional CSRF mitigation
- **Referer Validation**: Origin header verification for sensitive operations

### SQL Injection Prevention
- **Parameterized Queries**: All database operations use prepared statements
- **ORM Usage**: SQLAlchemy ORM for additional protection layer
- **Input Validation**: Strict validation before database operations

### Cross-Site Scripting (XSS) Prevention
- **Output Encoding**: All user content HTML-encoded
- **Content Security Policy**: Strict CSP headers implemented
- **Input Sanitization**: HTML content filtered and sanitized

## Audit & Compliance

### Comprehensive Audit Trail
```sql
-- Audit log structure
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);
```

#### Audited Events
- **Authentication**: Login attempts, password changes, account lockouts
- **Authorization**: Permission grants, role changes, access denials
- **Data Operations**: Image uploads, narrative edits, content deletions
- **Administrative Actions**: User management, system configuration changes
- **System Events**: Backup operations, security incidents, system errors

### HIPAA Compliance Features
- **Access Controls**: Role-based access with minimum necessary principle
- **Audit Trails**: Comprehensive logging of all PHI access
- **Data Integrity**: Checksums and validation for data integrity
- **Transmission Security**: Encrypted data transmission requirements
- **Breach Notification**: Automated alerts for potential security incidents

### Compliance Reporting
- **Access Reports**: Who accessed what data and when
- **Modification Reports**: All changes to patient data with timestamps
- **Security Reports**: Failed login attempts, permission changes
- **Export Capabilities**: Compliance reports in standard formats

## Incident Response

### Security Monitoring
- **Failed Login Tracking**: Automated detection of brute force attempts
- **Unusual Access Patterns**: Detection of abnormal user behavior
- **File Integrity Monitoring**: Detection of unauthorized file changes
- **System Resource Monitoring**: CPU, memory, and disk usage alerts

### Incident Response Procedures
1. **Detection**: Automated monitoring and manual reporting
2. **Assessment**: Severity classification and impact analysis
3. **Containment**: Immediate threat mitigation and system isolation
4. **Investigation**: Forensic analysis and root cause determination
5. **Recovery**: System restoration and security enhancement
6. **Documentation**: Incident reporting and lessons learned

### Breach Response Protocol
- **Immediate Containment**: System isolation and threat mitigation
- **Impact Assessment**: Determine scope of potential data exposure
- **Notification Requirements**: HIPAA breach notification procedures
- **Remediation**: Security improvements and system hardening
- **Documentation**: Complete incident documentation for compliance

## Network Security

### Deployment Security
- **Firewall Configuration**: Minimal port exposure (80, 443 only)
- **Network Segmentation**: Isolation from other hospital systems
- **VPN Access**: Secure remote administration access
- **Intrusion Detection**: Network-based monitoring and alerting

### API Security (Future)
- **OAuth 2.0**: Secure API authentication and authorization
- **Rate Limiting**: API abuse prevention and DoS mitigation
- **API Versioning**: Secure API evolution and deprecation
- **Input Validation**: Strict API parameter validation

## Security Configuration

### Production Security Checklist
- [ ] HTTPS enforced with valid certificates
- [ ] Database encryption enabled (SQLCipher)
- [ ] File system encryption configured
- [ ] Backup encryption implemented
- [ ] Audit logging enabled and monitored
- [ ] Password policies enforced
- [ ] Session security configured
- [ ] CSRF protection enabled
- [ ] Content Security Policy implemented
- [ ] Security headers configured
- [ ] Error handling secured (no information disclosure)
- [ ] Debug mode disabled
- [ ] Default credentials changed
- [ ] Unnecessary services disabled
- [ ] Security monitoring active

### Environment-Specific Security
```bash
# Production environment variables
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<generated-256-bit-key>
DATABASE_ENCRYPTION=True
AUDIT_LOGGING=True
HTTPS_ONLY=True
SESSION_COOKIE_SECURE=True
```

This security model ensures BHV meets healthcare industry standards while maintaining usability and system performance.