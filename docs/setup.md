# Setup & Environment Guide

## Supported Python Version

BHV requires **Python 3.8+** for optimal compatibility with healthcare network environments.

## Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv bhv-env

# Activate (Windows)
bhv-env\Scripts\activate

# Activate (Linux/macOS)
source bhv-env/bin/activate

# Install dependencies (when available)
pip install -r requirements.txt
```

### Using conda

```bash
# Create environment
conda create -n bhv python=3.8

# Activate
conda activate bhv

# Install dependencies (when available)
pip install -r requirements.txt
```

## Required System Dependencies

- **Python 3.8+**
- **SQLite3** (included with Python)
- **Pillow dependencies** (for image processing):
  - Windows: Usually included with Pillow
  - Ubuntu/Debian: `sudo apt-get install libjpeg-dev zlib1g-dev`
  - CentOS/RHEL: `sudo yum install libjpeg-devel zlib-devel`
  - macOS: `brew install libjpeg`

## Environment Configuration

The project uses a `.env` file for configuration. Copy the provided `.env.example` to a new file named `.env` and customize the values for your environment.

**Key variables to configure:**
- `SECRET_KEY`: **MUST** be changed to a unique, secret value in production
- `DEBUG`: Should be set to `False` in production
- `ALLOWED_HOSTS`: Should be configured with your domain/IP in production

See the comments within `.env.example` for more details on each variable.

## Directory Structure

The application will create these directories automatically:

```
BHV/
├── data/          # Database files
├── media/         # Uploaded images and files
│   └── uploads/   # User-uploaded content
├── logs/          # Application logs
└── .env           # Environment configuration
```

## Quick Start

1. Clone the repository
2. Set up virtual environment
3. Copy `.env.example` to `.env` and configure
4. Run: `python app.py` (single command startup)

## Security Notes

- **Generate a new SECRET_KEY** for production:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Set `DEBUG=False` in production environments
- Configure `ALLOWED_HOSTS` with your actual domain/IP addresses
- Ensure media directories are writable by the application user, and restrict access for other users
- Use HTTPS in production deployments