# BHV Implementation - Complete Application

This directory contains the **complete, working implementation** of the BHV (Behavioral Health Vault) application as specified in the project requirements.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python start.py
```

### 3. Access the Application
- Open your browser to: http://127.0.0.1:5000
- Default admin login:
  - Username: `admin`
  - Password: `admin123`
  - **⚠️ CHANGE THESE IMMEDIATELY!**

## 📁 Project Structure

```
BHV/
├── app.py                 # Main Flask application
├── start.py              # Startup script with checks
├── requirements.txt      # Python dependencies
├── 
├── config/               # Configuration management
│   ├── __init__.py
│   └── settings.py       # Environment & config handling
├── 
├── models/               # Database models
│   ├── __init__.py
│   └── database.py       # SQLite schema & operations
├── 
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── file_handler.py   # Secure file upload/storage
│   ├── auth.py          # Authentication & authorization
│   └── diagnostics.py   # System monitoring
├── 
├── templates/            # HTML templates
│   ├── base.html        # Base template with Bootstrap
│   ├── index.html       # Home page
│   ├── login.html       # Login form
│   ├── register.html    # Registration form
│   ├── dashboard.html   # User dashboard
│   ├── upload.html      # Image upload form
│   ├── admin.html       # Admin panel
│   └── diagnostics.html # System diagnostics
├── 
├── static/              # Static files (auto-created)
├── data/                # Database files (auto-created)
├── media/               # Uploaded files (auto-created)
├── logs/                # Application logs (auto-created)
└── tests/               # Test suite
    └── test_basic.py    # Basic functionality tests
```

## ✨ Features Implemented

### Core Functionality
- ✅ **User Authentication**: Email-based signup, username/password login
- ✅ **Image Upload**: Secure file upload with validation
- ✅ **Narrative Storage**: Text narratives associated with images
- ✅ **Role-Based Access**: Patient, Social Worker, Admin roles
- ✅ **Personal Gallery**: View/edit own content
- ✅ **Admin Dashboard**: System-wide management

### Security & Compliance
- ✅ **HIPAA-Compliant Design**: Audit trails, access controls
- ✅ **Secure File Handling**: File type validation, size limits
- ✅ **Password Security**: Strong password requirements, hashing
- ✅ **Session Management**: Secure sessions with timeout
- ✅ **Audit Logging**: Comprehensive activity tracking

### System Features
- ✅ **Single-Command Deployment**: `python start.py`
- ✅ **Automatic Setup**: Database initialization, directory creation
- ✅ **System Diagnostics**: Health monitoring, performance metrics
- ✅ **Configuration Management**: Environment-based configuration
- ✅ **Error Handling**: Comprehensive error management

### User Interface
- ✅ **Responsive Design**: Bootstrap-based UI
- ✅ **Minimal & Clean**: Healthcare-friendly interface
- ✅ **Accessibility**: Screen reader friendly
- ✅ **Progressive Enhancement**: Works without JavaScript

## 🔧 Configuration

### Environment Variables
Create a `.env` file or set environment variables:

```bash
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_PATH=data/bhv.db

# File Storage
UPLOAD_FOLDER=media/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Server
HOST=127.0.0.1
PORT=5000
DEBUG=False

# Security Settings
SESSION_TIMEOUT=3600
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,bmp,tiff

# Compliance
AUDIT_ENABLED=True
DATA_RETENTION_DAYS=2555  # 7 years
```

### Production Deployment
For production use:

1. **Set secure environment variables**:
   ```bash
   export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   export DEBUG=False
   export HOST=0.0.0.0
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up reverse proxy** (nginx/Apache)
4. **Configure SSL/TLS certificates**
5. **Set up regular backups**

## 🧪 Testing

### Run Basic Tests
```bash
python tests/test_basic.py
```

### Run with Test Mode
```bash
python start.py --test-only
```

### Skip Tests on Startup
```bash
python start.py --skip-tests
```

## 👥 User Roles & Permissions

### Patient
- Upload and manage personal images
- Add/edit personal narratives
- View own content only
- Private by default

### Social Worker
- View patient content (with permission)
- Add clinical notes to images
- Upload images on behalf of patients
- Content moderation capabilities

### Admin
- Full system access
- User management
- System diagnostics
- Content moderation
- Audit log access

## 🔒 Security Features

### Authentication
- Strong password requirements
- Secure password hashing (PBKDF2)
- Session management with timeout
- Login attempt monitoring

### File Security
- File type validation
- Size limits (16MB default)
- Secure filename generation
- Organized storage structure

### Compliance
- Comprehensive audit trails
- Role-based access control
- Data encryption at rest
- HIPAA-compliant design

## 📊 System Monitoring

### Health Checks
Access `/diagnostics` (admin only) for:
- System performance metrics
- Database health status
- File system monitoring
- Security status checks
- Configuration validation

### API Endpoints
- `/api/health` - Basic health check
- More endpoints available for integration

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors**
   ```bash
   # Ensure write permissions for:
   chmod 755 data/ media/ logs/
   ```

3. **Database Issues**
   ```bash
   # Delete and recreate database
   rm data/bhv.db
   python start.py
   ```

4. **Port Already in Use**
   ```bash
   export PORT=8000
   python start.py
   ```

### Debug Mode
Enable debug mode for development:
```bash
export DEBUG=True
python start.py
```

## 📈 Performance Optimization

### Database
- Automatic indexing on key fields
- Connection pooling
- Query optimization

### File Storage
- Organized directory structure
- Efficient file naming
- Optional thumbnail generation

### Caching
- Static file caching
- Session optimization
- Database query caching

## 🔄 Backup & Recovery

### Manual Backup
```bash
# Database backup
cp data/bhv.db data/backup_$(date +%Y%m%d).db

# File backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### Automated Backup
The admin panel includes backup functionality accessible via the diagnostics interface.

## 📝 Development

### Adding New Features
1. Follow the existing code structure
2. Add appropriate tests
3. Update documentation
4. Ensure security compliance

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include comprehensive docstrings
- Maintain security best practices

## 🆘 Support

### Getting Help
1. Check the troubleshooting section
2. Review the diagnostic output
3. Check application logs in `logs/bhv.log`
4. Verify configuration settings

### Reporting Issues
When reporting issues, include:
- System information
- Error messages
- Steps to reproduce
- Configuration (without secrets)

## 📄 License

This implementation follows the project's licensing terms and includes all necessary compliance features for healthcare environments.

---

**🏥 BHV: Behavioral Health Vault**  
*Secure, compliant, and user-friendly healthcare image storage*