# Contributing to BHV

Thank you for your interest in contributing to the Behavioral Health Vault project!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/BHV.git`
3. Create a branch: `git checkout -b feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Description of changes"`
7. Push to your fork: `git push origin feature-name`
8. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines for Python code
- Write meaningful commit messages
- Add docstrings to functions and classes
- Include tests for new features

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Describe your changes clearly in the PR description
4. Link any related issues
5. Wait for review from maintainers

## Questions?

Feel free to open an issue or start a discussion if you have questions!
```

4. Save

### **Step 6: Check Your Structure**

Your folder structure should now look like this:
```
BHV/
├── .gitignore
├── README.md (already exists)
├── requirements.txt
├── CONTRIBUTING.md
├── bhv/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── views/
│   │   └── __init__.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_basic.py
└── docs/
    └── installation.md