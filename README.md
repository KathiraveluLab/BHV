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


# BHV - Behavioral Health Vault

![Tests](https://github.com/KathiraveluLab/BHV/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)
![License](https://img.shields.io/badge/license-BSD--3--Clause-green)

> A simplified, secure approach to behavioral health documentation

## Features

✅ Secure image upload with multi-layer validation
✅ CSRF protection and filename sanitization
✅ SQLite database for easy deployment
✅ Automated testing with GitHub Actions
✅ 11 passing unit tests

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python bhv/app.py

# Open browser
http://localhost:5000
```

## Running Tests
```bash
# Run all tests
python -m pytest -v

# Should show: 11 passed
```

## CI/CD

This project uses GitHub Actions for automated testing on every push and pull request.

## Docker Deployment

BHV can be easily deployed using Docker!

### Quick Start
```bash
# Clone and run
git clone https://github.com/KathiraveluLab/BHV.git
cd BHV
docker-compose up -d
```

**Access:** http://localhost:5000

### What's Included

✅ Pre-configured Docker setup
✅ Persistent database and uploads
✅ Automatic health checks
✅ One-command deployment
✅ Works on Windows, Mac, Linux

### Full Documentation

See [DOCKER.md](DOCKER.md) for complete Docker deployment guide including:
- Development setup
- Production deployment
- Nginx configuration
- Backup/restore procedures
- Troubleshooting

### Requirements

- Docker (Get it: https://docs.docker.com/get-docker/)
- Docker Compose (included with Docker Desktop)

No Python installation needed! 🐳
