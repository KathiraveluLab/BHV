#  Developer Guide & Setup Documentation

## Part 1: Getting the Code

You can either **fork** the repository if you plan to contribute, or **clone** it if you only want to run the project locally.

### Step 1: Clone the Repository

Open your terminal (Command Prompt, PowerShell, or macOS/Linux Terminal) and run:

```bash
git clone https://github.com/Ramzan-Khan-786/bhv-vault
cd bhv-vault
```

---

## Part 2: Local Development Setup

### Step 2: Create and Activate a Virtual Environment

A virtual environment keeps project dependencies isolated from your global Python installation.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

If activation is successful, `(venv)` will appear at the beginning of your terminal prompt.

### Step 3: Install Dependencies

All required Python packages are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

##  Part 3: Environment Configuration (.env)

This application relies on **environment variables** to securely manage secrets such as keys, credentials, and database URLs.

### Step 4: Create the `.env` File

1. In the project root directory, create a file named `.env` (no file extension).
2. Add the following configuration template:

```ini
# --- SECURITY ---
# Secret key used for session encryption
SECRET_KEY=dev_key_replace_this_in_production

# --- DATABASE ---
# MongoDB connection string
MONGO_URI=mongodb://localhost:27017/my_local_db

# --- GOOGLE AUTHENTICATION ---
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# --- ADMIN BOOTSTRAP ---
# This user is promoted to ADMIN on first login
ADMIN_EMAIL=your_email@gmail.com
ADMIN_PASSWORD=admin123

# --- GITHUB INTEGRATION ---
# Personal Access Token for GitHub API access
GITHUB_TOKEN=Paste_Your_Github_Token

# GitHub Organization name (exact, case-sensitive)
ORG_NAME=Github_ORG_Name
```

For production, always replace development values with strong, unique secrets.

---

## Part 4: External Services Setup

### 1️ MongoDB Atlas (Database)

MongoDB Atlas is used to persist user and application data.

**Steps:**

1. Visit **MongoDB Atlas** and create an account or log in.
2. Create a **Shared Cluster (M0 – Free Tier)**.
3. Create a **Database User**:

   * Authentication Method: Username & Password
   * Save the credentials securely.
4. Configure **Network Access**:

   * Add IP Address: `0.0.0.0/0` (Allow access from anywhere)
5. Obtain the **Connection String**:

   * Go to *Database → Connect → Drivers (Python)*
   * Copy the connection URI
6. Update your `.env` file:

```ini
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/dbname
```

---

### 2️ Google OAuth Setup

Google OAuth enables users to authenticate using their Google accounts.

**Steps:**

1. Open **Google Cloud Console**.
2. Create a **New Project**.
3. Configure the **OAuth Consent Screen**:

   * User Type: External
   * Provide App Name and Support Email
4. Create **OAuth Client Credentials**:

   * Application Type: Web Application
   * Authorized Redirect URIs:

     * Local: `http://127.0.0.1:5001/login/google/callback`
     * Production: `https://your-app-name.onrender.com/login/google/callback`
5. Copy the **Client ID** and **Client Secret** into `.env`.

---

## Part 5: GitHub Token & Organization Setup

Some features require authenticated access to the GitHub API (for example, organization-level data or repository operations). This is handled using a GitHub Personal Access Token and your organization name.

### Step 5.1: Create a GitHub Personal Access Token

1. Log in to your GitHub account.
2. Go to **Settings → Developer Settings → Personal Access Tokens**.
3. Choose **Tokens (classic)** and click **Generate new token**.
4. Set:

   * Note: `Flask App Integration`
   * Expiration: As per your security preference
   * Scopes (minimum required):

     * `repo` (for private repositories)
     * `read:org` (to read organization information)
5. Generate the token and **copy it immediately** (you won’t see it again).

### Step 5.2: Get Your GitHub Organization Name

1. Open your GitHub organization page.
2. Copy the organization name exactly as it appears in the URL:

   * Example: `https://github.com/my-organization`
   * Organization name: `my-organization`

### Step 5.3: Update `.env`

Add the following entries to your `.env` file:

```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
ORG_NAME=my-organization
```

For production, add the same values in the **Render → Environment Variables** section.

---

##  Part 6: Production Deployment (Render)

Render is used to deploy the Flask application with HTTPS support and managed infrastructure.

### Step 5: Push Code to GitHub

Ensure your `.env` file is excluded using `.gitignore`.

```bash
git init
git add .
git commit -m "Initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/my-private-repo.git
git push -u origin main
```

### Step 6: Create a Render Web Service

1. Go to the **Render Dashboard**.
2. Select **New → Web Service**.
3. Connect your GitHub repository.
4. Configure settings:

   * Runtime: Python 3
   * Build Command: `pip install -r requirements.txt`
   * Start Command: `gunicorn "app:create_app()"`
5. Add all environment variables from `.env` into Render’s **Environment** tab.

---
## Troubleshooting

**Redirect URI Mismatch (Google OAuth)**

* Cause: Missing or incorrect redirect URI
* Fix: Add the correct production callback URL in Google Cloud Console

**Internal Server Error on Render**

* Cause: Missing environment variables
* Fix: Check Render logs and verify all required keys are set

**MongoDB Connection Refused**

* Cause: IP not whitelisted
* Fix: Ensure `0.0.0.0/0` is allowed in MongoDB Atlas Network Access

---