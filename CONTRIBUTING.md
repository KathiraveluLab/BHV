# Contributing to BHV

Thank you for your interest in contributing to BHV (Behavioral Health Vault)! This guide will help you get started.

## 📋 Table of Contents

1. [About BHV](#about-bhv)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Submitting Pull Requests](#submitting-pull-requests)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Getting Help](#getting-help)

---

## About BHV

BHV (Behavioral Health Vault) is a **minimal, secure platform** for behavioral health image documentation. It's designed for healthcare networks to help document serious mental illness recovery.

### Project Philosophy

BHV is **intentionally minimal**:
- ✅ Simple, focused features
- ✅ Security-first approach
- ✅ Easy to deploy
- ✅ HIPAA compliance oriented

**BHV is NOT "another Beehive"** - we prioritize simplicity and security over feature bloat.

---

## Getting Started

### Prerequisites

Before contributing, make sure you have:

- **Python 3.11+** installed
- **Git** installed
- **PostgreSQL** (for production-like testing) or SQLite (for quick development)
- **Text editor** (VS Code, PyCharm, Sublime, etc.)
- **GitHub account**

### Quick Start Checklist

- [ ] Read this guide completely
- [ ] Fork the repository
- [ ] Set up local development environment
- [ ] Make your changes
- [ ] Test your changes
- [ ] Submit a pull request

---

## Development Setup

### 1. Fork and Clone

**Fork the repository:**
1. Go to https://github.com/KathiraveluLab/BHV
2. Click "Fork" button (top right)
3. This creates your own copy

**Clone your fork:**
```bash
git clone https://github.com/YOUR-USERNAME/BHV.git
cd BHV
```

Replace `YOUR-USERNAME` with your GitHub username.

---

### 2. Create Virtual Environment

**Why?** Keeps dependencies isolated and clean.

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages.

---

### 4. Configure Environment Variables

**Create `.env` file:**

```bash
# Copy example (if exists) or create new
touch .env
```

**Add these variables:**

```bash
# Database (use SQLite for development)
DATABASE_URL=sqlite:///bhv_dev.db

# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Upload folder
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**⚠️ Important:** Never commit `.env` to Git! It's already in `.gitignore`.

---

### 5. Initialize Database

```bash
# Create database tables
flask db upgrade

# Or if no migrations exist:
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

---

### 6. Run Development Server

```bash
flask run
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
```

**Open browser:** http://localhost:5000

✅ **BHV is now running locally!**

---

## Making Changes

### 1. Create a New Branch

**Always create a new branch for your changes!**

```bash
# Make sure you're on main
git checkout main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

**Examples:**
- `feature/user-profile`
- `fix/login-redirect`
- `docs/deployment-guide`

---

### 2. Make Your Changes

**Edit the code using your favorite editor.**

**Keep changes focused:**
- ✅ One feature or fix per PR
- ✅ Related changes together
- ❌ Don't mix features and bug fixes
- ❌ Don't change unrelated files

---

### 3. Test Your Changes

**Manual testing:**
1. Run the app: `flask run`
2. Test your changes in browser
3. Try different scenarios
4. Check for errors in terminal

**Automated testing:**
```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=app
```

**Make sure all tests pass before submitting PR!**

---

### 4. Commit Your Changes

**Good commit messages are important!**

**Format:**
```
type: Brief description (50 chars or less)

Longer explanation if needed (wrap at 72 characters)
- What changed
- Why it changed
- Any important notes
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style/formatting (no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**

✅ **Good:**
```bash
git commit -m "feat: Add user profile page with bio and avatar"
```

✅ **Good:**
```bash
git commit -m "fix: Resolve PostgreSQL URL format issue on Render

Changed postgres:// to postgresql:// for SQLAlchemy 1.4+ compatibility.
This fixes deployment issues on Render.com and Heroku.
"
```

❌ **Bad:**
```bash
git commit -m "fixed stuff"
git commit -m "update"
git commit -m "changes"
```

---

## Submitting Pull Requests

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

---

### 2. Create Pull Request on GitHub

1. Go to https://github.com/KathiraveluLab/BHV
2. You'll see a yellow banner: "Compare & pull request"
3. Click it

**Or manually:**
1. Go to "Pull requests" tab
2. Click "New pull request"
3. Select your fork and branch

---

### 3. Fill Out PR Template

**Title:**
```
feat: Add user profile page
```

**Description:**

```markdown
## Overview
Brief description of what this PR does.

## Changes
- Added user profile page
- Created profile template
- Added profile route
- Updated navigation

## Testing
- [ ] Tested locally
- [ ] All existing tests pass
- [ ] Added new tests for profile page

## Screenshots (if UI changes)
[Add screenshots here]

## Related Issues
Closes #123 (if applicable)
```

---

### 4. Wait for Review

- ✅ Be patient - reviews take time
- ✅ Respond to feedback professionally
- ✅ Make requested changes promptly
- ✅ Ask questions if something is unclear

---

### 5. Address Feedback

**If reviewer requests changes:**

```bash
# Make the changes locally
# Test them

# Commit
git add .
git commit -m "fix: Address review feedback - improve error handling"

# Push to same branch
git push origin feature/your-feature-name
```

**PR updates automatically!**

---

## Code Style Guidelines

### Python Code (PEP 8)

**Follow PEP 8 standards:**

✅ **Good:**
```python
def calculate_total(items):
    """Calculate total price of items."""
    total = 0
    for item in items:
        total += item.price
    return total
```

❌ **Bad:**
```python
def CalculateTotal(items):
    total=0
    for item in items:total+=item.price
    return total
```

**Key rules:**
- Use 4 spaces for indentation (not tabs)
- Max line length: 79 characters
- Use snake_case for functions and variables
- Use PascalCase for classes
- Add docstrings to functions

**Check your code:**
```bash
# Install flake8
pip install flake8

# Check code
flake8 app.py
```

---

### HTML/Templates

**Use proper indentation:**

```html
<!-- Good -->
<div class="container">
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
</div>

<!-- Bad -->
<div class="container">
<h1>{{ title }}</h1>
<p>{{ content }}</p>
</div>
```

---

### CSS

**Keep it simple and organized:**

```css
/* Good */
.user-profile {
    padding: 20px;
    margin-bottom: 15px;
}

.user-profile h2 {
    color: #333;
    font-size: 24px;
}

/* Bad */
.user-profile{padding:20px;margin-bottom:15px;}
.user-profile h2{color:#333;font-size:24px;}
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

---

### Writing Tests

**Example test:**

```python
def test_user_registration(client):
    """Test user can register successfully."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword'
    })
    
    assert response.status_code == 302  # Redirect after success
    
    # Check user was created
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
```

**Test guidelines:**
- Write tests for new features
- Maintain >80% code coverage
- Test edge cases
- Test error handling

---

## Documentation

### When to Update Documentation

**Always update docs when you:**
- Add new features
- Change existing behavior
- Fix bugs that affect usage
- Add new configuration options
- Change API endpoints

### Types of Documentation

1. **Code comments** - Explain complex logic
2. **Docstrings** - Document functions and classes
3. **README.md** - Update if setup changes
4. **This file (CONTRIBUTING.md)** - Keep up to date
5. **Deployment guides** - Update for new deployment scenarios

---

## Getting Help

### Before Asking

1. **Search existing issues** - Your question might be answered
2. **Read documentation** - Check README and guides
3. **Check discussions** - See community Q&A

### How to Ask

**Open a discussion (preferred for questions):**
1. Go to https://github.com/KathiraveluLab/BHV/discussions
2. Click "New discussion"
3. Choose "Q&A" category
4. Provide clear title and description

**Create an issue (for bugs):**
1. Go to https://github.com/KathiraveluLab/BHV/issues
2. Click "New issue"
3. Describe the bug clearly
4. Include steps to reproduce
5. Add error messages if any

**Tag contributors for help:**
- @yadavchiragg - Deployment and documentation help
- @pradeeban - Project maintainer

---

## Pull Request Review Process

### What Happens After You Submit

1. **Automated checks** (if configured)
   - Tests run automatically
   - Code style checks

2. **Maintainer review**
   - Code quality review
   - Security review
   - Functionality check

3. **Feedback or approval**
   - Requested changes
   - Questions
   - Approval

4. **Merge**
   - PR gets merged into main branch
   - Your contribution is live!

### Review Timeline

- **Documentation PRs:** 3-7 days
- **Bug fixes:** 2-5 days
- **New features:** 5-14 days

**Be patient!** Maintainers are often busy with other responsibilities.

---

## Important Notes

### What We Look For

✅ **Good PRs:**
- Clear, focused changes
- Well-tested
- Good documentation
- Clean code
- Helpful commit messages

❌ **Avoid:**
- Large, unfocused PRs
- Breaking changes without discussion
- Code without tests
- Undocumented changes
- Style-only changes (unless requested)

### Current Focus Areas

**We're currently prioritizing:**
1. Security hardening (HIPAA compliance)
2. Performance optimization
3. Deployment documentation
4. Testing coverage

**Features on hold:**
- Complex new features
- UI/UX overhauls
- Third-party integrations

**Why?** We want BHV to be minimal, secure, and production-ready before adding more features.

---

## Code of Conduct

### Be Respectful

- ✅ Professional communication
- ✅ Constructive feedback
- ✅ Patience with reviewers
- ✅ Help other contributors

### Unacceptable Behavior

- ❌ Harassment or discrimination
- ❌ Spam or self-promotion
- ❌ Disrespectful comments
- ❌ Sharing others' private information

---

## Recognition

### Contributors

All contributors are listed in:
- GitHub contributors page
- Project documentation (if significant contribution)
- Release notes (for major features)

### Your First PR

**First-time contributors** get extra support and guidance! Don't hesitate to ask questions.

---

## Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Python PEP 8:** https://pep8.org/
- **Git Basics:** https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- **GitHub Flow:** https://guides.github.com/introduction/flow/

---

## Quick Reference

### Common Commands

```bash
# Start development server
flask run

# Run tests
pytest

# Check code style
flake8 .

# Create migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## Contact

- **GitHub Discussions:** https://github.com/KathiraveluLab/BHV/discussions
- **Issues:** https://github.com/KathiraveluLab/BHV/issues
- **Project Maintainer:** @pradeeban

---

## License

By contributing to BHV, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to BHV! Your help makes healthcare technology more accessible and secure.** 🚀

---

**Last Updated:** January 2026  
**Maintained by:** BHV Community
