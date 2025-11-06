# Authentication & Authorization System

## Overview
This document describes the complete authentication and authorization system for BHV.

## Authentication Flow

### 1. Registration
- **Only regular users** can register through the registration form
- User registers with email and password (no role selection)
- Admin emails are prevented from registration via form validation
- OTP code is generated and sent via email (or console if email not configured)
- User must verify OTP before accessing protected routes
- After verification, user is automatically logged in

### 2. Admin Account Creation
- Admin accounts are **NOT** created through registration
- Admin emails must be configured in `.env` file: `ADMIN_EMAILS=admin1@example.com,admin2@example.com`
- Admin users can be created via:
  1. **Google OAuth**: If admin email logs in via Google OAuth, account is automatically created with admin role
  2. **Manual script**: Use `python create_admin.py <email> <password>` (email must be in ADMIN_EMAILS)
- Role is automatically determined from `ADMIN_EMAILS` list

### 3. Login
- **Verified users**: Login with email and password (no OTP required)
- **Unverified users**: Redirected to registration to complete verification
- Supports Google OAuth as alternative login method
- If admin email logs in via Google OAuth, account is automatically created with admin role

### 4. Email Verification
- OTP required only during initial registration
- OTP expires after 10 minutes (configurable)
- Each OTP can only be used once
- Users cannot access protected routes until verified

## Authorization System

### Role-Based Access Control (RBAC)

#### Roles
- **user**: Regular users with limited access (default for all registrations)
- **admin**: Administrators with full access to all features
  - Admin role is **dynamically checked** from `ADMIN_EMAILS` in `.env`
  - If a user's email is in `ADMIN_EMAILS`, they are treated as admin **at runtime**
  - This means you can add an email to `ADMIN_EMAILS` and the user immediately gets admin access without database changes
  - Cannot be obtained through registration form
  - Must be configured in `ADMIN_EMAILS` environment variable

**Important**: The role check is dynamic - it always checks `ADMIN_EMAILS` at runtime. If you add a user's email to `ADMIN_EMAILS` in `.env`, they will immediately have admin privileges without needing to modify the database.

### Decorators

#### `@verified_user_required`
- **Purpose**: Ensures user is logged in AND email is verified
- **Used on**: All protected routes (uploads, gallery, chat, etc.)
- **Behavior**: 
  - Redirects to login if not authenticated
  - Redirects to registration if email not verified
  - Allows access if verified

#### `@admin_required`
- **Purpose**: Restricts access to admin users only
- **Used on**: Admin dashboard, admin routes, admin-only API endpoints
- **Behavior**:
  - Checks authentication and verification
  - Checks if user role is 'admin'
  - Returns 403 error (API) or redirects to gallery (web)
  - Allows access if admin

## Protected Routes

### User Routes (Require `@verified_user_required`)
- `/uploads/upload` - Upload content
- `/uploads/gallery` - View gallery
- `/uploads/detail/<id>` - View upload details
- `/uploads/file/image/<id>` - Serve images
- `/uploads/file/audio/<id>` - Serve audio files
- `/chat/send` - Send chat messages
- `/chat/list/<user_id>` - View user's messages
- `/auth/logout` - Logout

### Admin Routes (Require `@admin_required`)
- `/admin/dashboard` - Admin dashboard with statistics
- `/admin/all-uploads` - View all uploads
- `/chat/list` - View all chat messages (admin only)

### Public Routes (No authentication required)
- `/` - Home/index page
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/auth/verify-otp` - OTP verification page
- `/auth/google-login` - Google OAuth initiation
- `/auth/google-callback` - Google OAuth callback

## Security Features

### Password Security
- Passwords are hashed using bcrypt
- Minimum 6 characters required
- Passwords are never stored in plain text

### Session Security
- Uses Flask-Login for session management
- Strong session protection enabled
- Sessions require authentication

### Email Verification
- OTP-based email verification
- Prevents unauthorized account access
- Expires after configured time

### Authorization Checks
- All protected routes verify:
  1. User is authenticated
  2. Email is verified
  3. User has required role (for admin routes)

## Google OAuth

### Features
- Alternative login method
- Automatically creates account if user doesn't exist
- Links Google account to existing email if found
- Google users are automatically verified (no OTP needed)

### Configuration
- Requires `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Redirect URI must be configured in Google Cloud Console

## Access Control Matrix

| Route | Public | User (Verified) | Admin (Verified) |
|-------|--------|----------------|------------------|
| `/auth/login` | ✅ | ✅ | ✅ |
| `/auth/register` | ✅ | ✅ | ✅ |
| `/uploads/gallery` | ❌ | ✅ | ✅ |
| `/uploads/upload` | ❌ | ✅ | ✅ |
| `/admin/dashboard` | ❌ | ❌ | ✅ |
| `/admin/all-uploads` | ❌ | ❌ | ✅ |
| `/chat/send` | ❌ | ✅ | ✅ |
| `/chat/list` | ❌ | ❌ | ✅ |

## Error Handling

### Unauthenticated Users
- Redirected to login page
- Flash message: "Please log in to access this page."

### Unverified Users
- Redirected to registration page
- Flash message: "Please verify your email before accessing this page."

### Unauthorized Access (Non-admin accessing admin routes)
- Redirected to gallery (web routes)
- Returns 403 error (API routes)
- Flash message: "Admin access required."

## Implementation Files

### Core Authentication
- `app/auth/routes.py` - Authentication routes (login, register, OTP)
- `app/auth/forms.py` - Form definitions for authentication
- `app/auth/decorators.py` - Authorization decorators

### Models
- `app/models.py` - User, OTP, Upload, ChatMessage models

### Configuration
- `app/config.py` - Application configuration including auth settings
  - `Config.ADMIN_EMAILS` - List of admin email addresses from environment
  - `Config.is_admin_email(email)` - Method to check if email is admin
- `.env` - Environment variables for secrets
  - **ADMIN_EMAILS**: Comma-separated list of admin email addresses
  - Only emails in this list will be assigned admin role
  - Example: `ADMIN_EMAILS=admin1@example.com,admin2@example.com`

## Best Practices

1. **Always verify email** before allowing access to protected routes
2. **Check role** for admin-only functionality
3. **Validate input** on all forms
4. **Hash passwords** - never store plain text
5. **Use decorators** consistently for authorization
6. **Log security events** for monitoring

## Testing Authentication

### Manual Testing Steps
1. Register a new user → Should receive OTP
2. Verify OTP → Should be logged in
3. Try accessing protected route without login → Should redirect to login
4. Login with verified account → Should access protected routes
5. Try accessing admin route as regular user → Should be denied
6. Add admin email to `.env` → `ADMIN_EMAILS=admin@example.com`
7. Create admin user → `python create_admin.py admin@example.com admin123`
8. Login as admin → Should access admin routes

### Test Users
Run `python seed_data.py` to create test users:
- User: `user@example.com` / `user123`

### Creating Admin Users
1. Add admin email to `.env`: `ADMIN_EMAILS=admin@example.com`
2. Run: `python create_admin.py admin@example.com admin123`
3. Login with admin credentials

