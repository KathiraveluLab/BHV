# Authentication Flow

## Users Authentication
- **Email and Password**
- **Google OAuth (Optional Quick Login)**

###  Signup Requirements
- Email Address (**must be unique**)
- Password (**minimum 6 characters**)

> No username, no phone number, and no extra verification steps are required.


###  User Login
- Email  
- Password  



##  Implementation Details
- User credentials stored securely in **MongoDB**
- Session based authentication
- Passwords are **hashed using bcrypt**
- **Email uniqueness validation**
- Basic **rate limiting** on login to prevent abuse



## Google Login Flow
1. User clicks **“Continue with Google”**
2. Google authentication popup opens
3. User selects Google account
4. BHV receives:
   - Google ID  
   - Name  
   - Email  
5. If user already exists → **Login**
6. If new user → **Account is auto-created**
7. Session is created and user is redirected to **Dashboard**

##  Unified User Session Structure

All authenticated users share the same session structure.

```json
{
  "user_id": "ObjectId",
  "email": "user@example.com",
  "auth_provider": "local | google",
  "login_time": "ISO-8601"
}
```
## Admin Authentication

- Administrators will be added as collaborators, ensuring they can view, edit, and moderate submissions, while other users repositories remain private and isolated.
